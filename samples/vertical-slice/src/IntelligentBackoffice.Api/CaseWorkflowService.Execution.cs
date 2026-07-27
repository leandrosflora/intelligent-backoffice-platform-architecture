namespace IntelligentBackoffice.Api;

public sealed partial class CaseWorkflowService
{
    public Task<ServiceResult> RequestExecutionAsync(
        ApiRequestContext context,
        Guid caseId,
        ExecutionRequest request,
        CancellationToken cancellationToken)
    {
        ValidateExecution(request);

        return MutateAsync(
            context, caseId, "execution.request", request, request.CaseVersion,
            StatusCodes.Status202Accepted,
            aggregate => new
            {
                case_version = aggregate.CaseVersion,
                approval_status = aggregate.Approval?.Status ?? "",
                approval_valid = aggregate.Approval?.ExpiresAt > DateTimeOffset.UtcNow,
                recommendation_version = aggregate.Recommendation?.RecommendationVersion ?? 0,
                approved_recommendation_version = aggregate.Approval?.RecommendationVersion ?? 0,
                idempotency_key = context.IdempotencyKey ?? "",
                command_hash = request.CommandHash,
                evidence_references = request.EvidenceReferences
            },
            (aggregate, _) =>
            {
                EnsureState(aggregate, "APPROVED");
                if (aggregate.Approval is null
                    || aggregate.Approval.ApprovalId != request.ApprovalId
                    || aggregate.Approval.Status != "APPROVED")
                {
                    throw new ApiException(StatusCodes.Status422UnprocessableEntity,
                        "approval-required", "Aprovação válida e compatível é obrigatória.");
                }

                if (aggregate.Recommendation?.RecommendationVersion != request.RecommendationVersion)
                {
                    throw new ApiException(StatusCodes.Status409Conflict,
                        "recommendation-version-conflict",
                        "Versão da recomendação não corresponde à aprovação.");
                }

                var ambiguous = request.CommandHash.StartsWith("0000", StringComparison.OrdinalIgnoreCase);
                var now = DateTimeOffset.UtcNow;
                var execution = new ExecutionRecord
                {
                    ExecutionId = Guid.NewGuid(),
                    CaseId = aggregate.CaseId,
                    Status = ambiguous ? "RECONCILIATION_REQUIRED" : "SUCCEEDED",
                    IdempotencyKey = RequireIdempotencyKey(context),
                    CommandHash = request.CommandHash.ToLowerInvariant(),
                    ExternalReference = ambiguous ? null : $"MOCK-{Guid.NewGuid():N}",
                    CreatedAt = now,
                    CompletedAt = ambiguous ? null : now
                };

                aggregate.Executions.Add(execution);
                aggregate.State = ambiguous ? "RECONCILIATION_REQUIRED" : "EXECUTED";

                return new MutationPlan(
                    execution,
                    ambiguous
                        ? [
                            new MutationEvent("EXECUTION_REQUESTED", null,
                                "backoffice.execution.requested.v1"),
                            new MutationEvent("RECONCILIATION_REQUIRED",
                                "O mock simulou resposta ambígua.",
                                "backoffice.reconciliation.required.v1")
                          ]
                        : [
                            new MutationEvent("EXECUTION_REQUESTED", null,
                                "backoffice.execution.requested.v1"),
                            new MutationEvent("EXECUTION_COMPLETED",
                                "Operação mock concluída.",
                                "backoffice.execution.completed.v1")
                          ]);
            },
            cancellationToken);
    }

    public async Task<ServiceResult> GetExecutionAsync(
        ApiRequestContext context,
        Guid caseId,
        Guid executionId,
        CancellationToken cancellationToken)
    {
        await using var connection = await _store.OpenConnectionAsync(cancellationToken);
        var aggregate = await RequireCaseAsync(
            connection, null, context.TenantId, caseId, false, cancellationToken);
        await AuthorizeAsync(context, "execution.read", aggregate.State,
            new { case_version = aggregate.CaseVersion }, cancellationToken);

        var execution = aggregate.Executions.SingleOrDefault(item => item.ExecutionId == executionId)
            ?? throw new ApiException(StatusCodes.Status404NotFound,
                "execution-not-found", "Execução não encontrada.");
        return new ServiceResult(StatusCodes.Status200OK, aggregate.CaseVersion, execution);
    }

    public Task<ServiceResult> ResolveReconciliationAsync(
        ApiRequestContext context,
        Guid caseId,
        Guid executionId,
        ReconciliationResolutionRequest request,
        CancellationToken cancellationToken)
    {
        if (request.Resolution is not ("CONFIRMED_SUCCEEDED" or "CONFIRMED_FAILED" or "ESCALATED")
            || string.IsNullOrWhiteSpace(request.Reason))
        {
            throw new ApiException(StatusCodes.Status400BadRequest,
                "invalid-reconciliation", "Resolução e motivo válidos são obrigatórios.");
        }

        return MutateAsync(
            context, caseId, "reconciliation.resolve", request, request.CaseVersion,
            StatusCodes.Status200OK,
            aggregate => new { case_version = aggregate.CaseVersion },
            (aggregate, _) =>
            {
                EnsureState(aggregate, "RECONCILIATION_REQUIRED");
                var execution = aggregate.Executions
                    .SingleOrDefault(item => item.ExecutionId == executionId)
                    ?? throw new ApiException(StatusCodes.Status404NotFound,
                        "execution-not-found", "Execução não encontrada.");

                if (execution.Status != "RECONCILIATION_REQUIRED")
                {
                    throw new ApiException(StatusCodes.Status422UnprocessableEntity,
                        "reconciliation-not-required", "A execução não exige reconciliação.");
                }

                switch (request.Resolution)
                {
                    case "CONFIRMED_SUCCEEDED":
                        execution.Status = "RECONCILED";
                        execution.CompletedAt = DateTimeOffset.UtcNow;
                        execution.ExternalReference = $"MOCK-RECON-{Guid.NewGuid():N}";
                        aggregate.State = "EXECUTED";
                        break;
                    case "CONFIRMED_FAILED":
                        execution.Status = "FAILED";
                        execution.CompletedAt = DateTimeOffset.UtcNow;
                        aggregate.State = "FAILED";
                        break;
                    default:
                        aggregate.State = "RECONCILIATION_REQUIRED";
                        break;
                }

                return new MutationPlan(
                    execution,
                    [new MutationEvent("RECONCILIATION_RESOLVED", request.Reason,
                        request.Resolution == "CONFIRMED_FAILED"
                            ? "backoffice.execution.failed.v1"
                            : "backoffice.execution.completed.v1")]);
            },
            cancellationToken);
    }

    public async Task<ServiceResult> GetTimelineAsync(
        ApiRequestContext context,
        Guid caseId,
        CancellationToken cancellationToken)
    {
        await using var connection = await _store.OpenConnectionAsync(cancellationToken);
        var aggregate = await RequireCaseAsync(
            connection, null, context.TenantId, caseId, false, cancellationToken);
        await AuthorizeAsync(context, "audit.read", aggregate.State,
            new { case_version = aggregate.CaseVersion }, cancellationToken);
        var timeline = await _store.GetTimelineAsync(
            connection, context.TenantId, caseId, cancellationToken);
        return new ServiceResult(StatusCodes.Status200OK, aggregate.CaseVersion, timeline);
    }

}
