using System.Text.Json;

namespace IntelligentBackoffice.Api;

public sealed partial class CaseWorkflowService
{
    public async Task<ServiceResult> CreateCaseAsync(
        ApiRequestContext context,
        CreateCaseRequest request,
        CancellationToken cancellationToken)
    {
        ValidateCreateCase(request);
        var key = RequireIdempotencyKey(context);
        var scope = "case.create";
        var requestHash = HashRequest(request);

        await using var connection = await _store.OpenConnectionAsync(cancellationToken);
        await using var transaction = await connection.BeginTransactionAsync(cancellationToken);

        var cached = await _store.GetIdempotencyAsync(
            connection, transaction, context.TenantId, scope, key, cancellationToken);
        if (cached is not null)
        {
            EnsureSameRequest(cached, requestHash);
            return new ServiceResult(
                StatusCodes.Status200OK, null, RawJson: cached.ResponseBody, Replay: true);
        }

        var existing = await _store.GetCaseByExternalReferenceAsync(
            connection, transaction, context.TenantId, request.ExternalReference, cancellationToken);

        if (existing is not null)
        {
            if (!Equivalent(existing, request))
            {
                throw new ApiException(StatusCodes.Status409Conflict,
                    "external-reference-conflict",
                    "A referência externa já existe com conteúdo diferente.");
            }

            var existingJson = JsonSerializer.Serialize(existing.ToView(), JsonDefaults.Options);
            await _store.SaveIdempotencyAsync(
                connection, transaction, context.TenantId, scope, key,
                requestHash, StatusCodes.Status200OK, existingJson, cancellationToken);
            await transaction.CommitAsync(cancellationToken);
            return new ServiceResult(
                StatusCodes.Status200OK, existing.CaseVersion,
                existing.ToView(), Replay: true,
                Location: $"/v1/cases/{existing.CaseId}");
        }

        await AuthorizeAsync(context, "case.create", "CREATED", new { }, cancellationToken);

        var now = DateTimeOffset.UtcNow;
        var aggregate = new CaseAggregate
        {
            CaseId = Guid.NewGuid(),
            TenantId = context.TenantId,
            ExternalReference = request.ExternalReference.Trim(),
            DisputeType = request.DisputeType,
            Channel = request.Channel,
            State = "CREATED",
            CaseVersion = 1,
            Priority = "NORMAL",
            DisputedAmount = request.DisputedAmount,
            CustomerReference = request.CustomerReference,
            CreatedAt = now,
            UpdatedAt = now
        };

        await _store.InsertCaseAsync(connection, transaction, aggregate, cancellationToken);
        await AppendArtifactsAsync(
            connection, transaction, context, aggregate,
            [new MutationEvent("CASE_CREATED", "Caso registrado.", "backoffice.case.created.v1")],
            cancellationToken);

        var response = aggregate.ToView();
        var responseJson = JsonSerializer.Serialize(response, JsonDefaults.Options);
        await _store.SaveIdempotencyAsync(
            connection, transaction, context.TenantId, scope, key,
            requestHash, StatusCodes.Status201Created, responseJson, cancellationToken);

        await transaction.CommitAsync(cancellationToken);
        return new ServiceResult(
            StatusCodes.Status201Created, aggregate.CaseVersion, response,
            Location: $"/v1/cases/{aggregate.CaseId}");
    }

    public async Task<ServiceResult> GetCaseAsync(
        ApiRequestContext context,
        Guid caseId,
        CancellationToken cancellationToken)
    {
        await using var connection = await _store.OpenConnectionAsync(cancellationToken);
        var aggregate = await RequireCaseAsync(
            connection, null, context.TenantId, caseId, false, cancellationToken);
        await AuthorizeAsync(context, "case.read", aggregate.State,
            new { case_version = aggregate.CaseVersion }, cancellationToken);
        return new ServiceResult(StatusCodes.Status200OK, aggregate.CaseVersion, aggregate.ToView());
    }

    public Task<ServiceResult> CancelCaseAsync(
        ApiRequestContext context,
        Guid caseId,
        CancelCaseRequest request,
        CancellationToken cancellationToken)
    {
        if (string.IsNullOrWhiteSpace(request.Reason))
        {
            throw new ApiException(StatusCodes.Status400BadRequest,
                "reason-required", "Motivo obrigatório.");
        }

        return MutateAsync(
            context, caseId, "case.cancel", request, context.ExpectedVersion ?? 0,
            StatusCodes.Status200OK,
            aggregate => new { case_version = aggregate.CaseVersion },
            (aggregate, _) =>
            {
                EnsureState(aggregate,
                    "CREATED", "AWAITING_DOCUMENTS", "DOCUMENTS_RECEIVED", "DOCUMENTS_VALIDATED");
                aggregate.State = "CANCELLED";
                return new MutationPlan(
                    aggregate.ToView(),
                    [new MutationEvent("CASE_CANCELLED", request.Reason)]);
            },
            cancellationToken);
    }

}
