using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Npgsql;

namespace IntelligentBackoffice.Api;

public sealed partial class CaseWorkflowService
{
    private static readonly HashSet<string> DisputeTypes =
        ["CARD_PURCHASE", "PIX", "TRANSFER", "CASH_WITHDRAWAL", "OTHER"];

    private static readonly HashSet<string> Channels =
        ["APP", "WEB", "CONTACT_CENTER", "BRANCH", "API"];

    private static readonly HashSet<string> DocumentTypes =
        ["RECEIPT", "STATEMENT", "TRANSACTION_PROOF", "IDENTITY_PROOF", "OTHER"];

    private static readonly HashSet<string> MediaTypes =
        ["application/pdf", "image/png", "image/jpeg"];

    private static readonly HashSet<string> InvestigationChecks =
        ["TRANSACTION_LOOKUP", "FRAUD_SIGNAL_LOOKUP", "CUSTOMER_HISTORY", "DOCUMENT_CONSISTENCY"];

    private readonly PostgresStore _store;
    private readonly OpaAuthorizationClient _opa;

    public CaseWorkflowService(PostgresStore store, OpaAuthorizationClient opa)
    {
        _store = store;
        _opa = opa;
    }

    private async Task<ServiceResult> MutateAsync(
        ApiRequestContext context,
        Guid caseId,
        string action,
        object request,
        int requestCaseVersion,
        int successStatus,
        Func<CaseAggregate, object> policyContextFactory,
        Func<CaseAggregate, int, MutationPlan> mutation,
        CancellationToken cancellationToken)
    {
        var key = RequireIdempotencyKey(context);
        var scope = $"{action}:{caseId}";
        var requestHash = HashRequest(request);

        await using var connection = await _store.OpenConnectionAsync(cancellationToken);
        await using var transaction = await connection.BeginTransactionAsync(cancellationToken);

        var cached = await _store.GetIdempotencyAsync(
            connection, transaction, context.TenantId, scope, key, cancellationToken);
        if (cached is not null)
        {
            EnsureSameRequest(cached, requestHash);
            return new ServiceResult(
                cached.ResponseStatus, null,
                RawJson: cached.ResponseBody, Replay: true);
        }

        var aggregate = await RequireCaseAsync(
            connection, transaction, context.TenantId, caseId, true, cancellationToken);

        var expectedVersion = context.ExpectedVersion
            ?? throw new ApiException(StatusCodes.Status400BadRequest,
                "if-match-required", "If-Match obrigatório.");

        if (expectedVersion != aggregate.CaseVersion
            || requestCaseVersion != aggregate.CaseVersion)
        {
            throw new ApiException(StatusCodes.Status409Conflict,
                "case-version-conflict",
                $"Versão esperada {expectedVersion}; versão atual {aggregate.CaseVersion}.");
        }

        await AuthorizeAsync(
            context, action, aggregate.State,
            policyContextFactory(aggregate), cancellationToken);

        var currentVersion = aggregate.CaseVersion;
        var nextVersion = currentVersion + 1;
        aggregate.CaseVersion = nextVersion;
        aggregate.UpdatedAt = DateTimeOffset.UtcNow;
        var plan = mutation(aggregate, nextVersion);

        await _store.UpdateCaseAsync(
            connection, transaction, aggregate, currentVersion, cancellationToken);
        await AppendArtifactsAsync(
            connection, transaction, context, aggregate, plan.Events, cancellationToken);

        var responseJson = JsonSerializer.Serialize(plan.Response, JsonDefaults.Options);
        await _store.SaveIdempotencyAsync(
            connection, transaction, context.TenantId, scope, key,
            requestHash, successStatus, responseJson, cancellationToken);

        await transaction.CommitAsync(cancellationToken);
        return new ServiceResult(successStatus, aggregate.CaseVersion, plan.Response);
    }

    private async Task AppendArtifactsAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction,
        ApiRequestContext context,
        CaseAggregate aggregate,
        IReadOnlyList<MutationEvent> events,
        CancellationToken cancellationToken)
    {
        foreach (var item in events)
        {
            var entry = new TimelineEntry
            {
                EntryId = Guid.NewGuid(),
                CaseId = aggregate.CaseId,
                CaseVersion = aggregate.CaseVersion,
                Type = item.Type,
                ActorId = context.Subject.Id,
                Reason = item.Reason,
                OccurredAt = DateTimeOffset.UtcNow,
                CorrelationId = context.CorrelationId
            };

            await _store.AppendTimelineAsync(
                connection, transaction, context.TenantId, entry, cancellationToken);

            if (!string.IsNullOrWhiteSpace(item.EventType))
            {
                await _store.AppendOutboxAsync(
                    connection, transaction, context, aggregate, item.EventType,
                    cancellationToken);
            }
        }
    }

    private async Task AuthorizeAsync(
        ApiRequestContext context,
        string action,
        string state,
        object policyContext,
        CancellationToken cancellationToken)
    {
        var decision = await _opa.DecideAsync(
            context, action, state, policyContext, cancellationToken);
        if (!decision.Allow)
        {
            throw new ApiException(StatusCodes.Status403Forbidden,
                "policy-denied", $"Policy negou {action}: {decision.Reason}.");
        }
    }

    private async Task<CaseAggregate> RequireCaseAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction? transaction,
        Guid tenantId,
        Guid caseId,
        bool forUpdate,
        CancellationToken cancellationToken)
    {
        return await _store.GetCaseAsync(
            connection, transaction, tenantId, caseId, forUpdate, cancellationToken)
            ?? throw new ApiException(StatusCodes.Status404NotFound,
                "case-not-found", "Caso não encontrado.");
    }

    private static void EnsureState(CaseAggregate aggregate, params string[] allowed)
    {
        if (!allowed.Contains(aggregate.State, StringComparer.Ordinal))
        {
            throw new ApiException(StatusCodes.Status422UnprocessableEntity,
                "invalid-state",
                $"Estado {aggregate.State} não permite esta operação.");
        }
    }

    private static string RequireIdempotencyKey(ApiRequestContext context) =>
        !string.IsNullOrWhiteSpace(context.IdempotencyKey)
            ? context.IdempotencyKey
            : throw new ApiException(StatusCodes.Status400BadRequest,
                "idempotency-key-required", "Idempotency-Key obrigatória.");

    private static void EnsureSameRequest(IdempotencyRecord cached, string requestHash)
    {
        if (!CryptographicOperations.FixedTimeEquals(
                Convert.FromHexString(cached.RequestHash),
                Convert.FromHexString(requestHash)))
        {
            throw new ApiException(StatusCodes.Status409Conflict,
                "idempotency-conflict",
                "A mesma Idempotency-Key foi utilizada com payload diferente.");
        }
    }

    private static string HashRequest(object request)
    {
        var json = JsonSerializer.Serialize(request, JsonDefaults.Options);
        return Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(json)))
            .ToLowerInvariant();
    }

    private static bool Equivalent(CaseAggregate aggregate, CreateCaseRequest request) =>
        aggregate.ExternalReference == request.ExternalReference.Trim()
        && aggregate.DisputeType == request.DisputeType
        && aggregate.Channel == request.Channel
        && aggregate.DisputedAmount.Currency == request.DisputedAmount.Currency
        && aggregate.DisputedAmount.Amount == request.DisputedAmount.Amount;

    private static void ValidateCreateCase(CreateCaseRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.ExternalReference)
            || !DisputeTypes.Contains(request.DisputeType)
            || !Channels.Contains(request.Channel))
        {
            throw new ApiException(StatusCodes.Status400BadRequest,
                "invalid-case", "externalReference, disputeType e channel são obrigatórios.");
        }

        if (request.DisputedAmount.Currency.Length != 3
            || request.DisputedAmount.AsDecimal() <= 0)
        {
            throw new ApiException(StatusCodes.Status400BadRequest,
                "invalid-amount", "disputedAmount deve ser positivo.");
        }
    }

    private static void ValidateDocument(RegisterDocumentRequest request)
    {
        if (!DocumentTypes.Contains(request.DocumentType)
            || !MediaTypes.Contains(request.MediaType)
            || request.Checksum.Length != 64
            || request.Checksum.Any(character => !Uri.IsHexDigit(character))
            || string.IsNullOrWhiteSpace(request.StorageReference))
        {
            throw new ApiException(StatusCodes.Status400BadRequest,
                "invalid-document", "Metadados do documento são inválidos.");
        }
    }

    private static void ValidateExecution(ExecutionRequest request)
    {
        if (request.CommandType is not ("MOCK_REFUND" or "MOCK_REVERSAL")
            || request.CommandHash.Length != 64
            || request.CommandHash.Any(character => !Uri.IsHexDigit(character))
            || request.EvidenceReferences.Count == 0)
        {
            throw new ApiException(StatusCodes.Status400BadRequest,
                "invalid-execution", "Comando de execução inválido.");
        }
    }
}
