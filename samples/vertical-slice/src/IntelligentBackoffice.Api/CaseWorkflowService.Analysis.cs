namespace IntelligentBackoffice.Api;

public sealed partial class CaseWorkflowService
{
    public Task<ServiceResult> StartInvestigationAsync(
        ApiRequestContext context,
        Guid caseId,
        InvestigationRequest request,
        CancellationToken cancellationToken)
    {
        if (request.RequestedChecks.Count == 0
            || request.RequestedChecks.Any(check => !InvestigationChecks.Contains(check)))
        {
            throw new ApiException(StatusCodes.Status400BadRequest,
                "invalid-investigation-checks", "requestedChecks contém valor inválido.");
        }

        return MutateAsync(
            context, caseId, "investigation.execute", request, request.CaseVersion,
            StatusCodes.Status202Accepted,
            aggregate => new
            {
                case_version = aggregate.CaseVersion,
                evidence_references = aggregate.Evidence.Select(item => item.EvidenceId).ToArray()
            },
            (aggregate, _) =>
            {
                EnsureState(aggregate, "DOCUMENTS_VALIDATED");
                if (aggregate.Evidence.Count == 0)
                {
                    throw new ApiException(StatusCodes.Status422UnprocessableEntity,
                        "evidence-required", "A investigação exige evidências.");
                }

                var now = DateTimeOffset.UtcNow;
                var investigation = new InvestigationRecord
                {
                    InvestigationId = Guid.NewGuid(),
                    CaseId = aggregate.CaseId,
                    Status = "COMPLETED",
                    Findings =
                    [
                        new FindingRecord
                        {
                            Kind = "CONFIRMED_FACT",
                            Summary = "Documento sintético validado e transação mock localizada.",
                            EvidenceReferences = aggregate.Evidence
                                .Select(item => item.EvidenceId).ToList()
                        }
                    ],
                    CreatedAt = now,
                    CompletedAt = now
                };

                aggregate.Investigation = investigation;
                aggregate.State = "UNDER_INVESTIGATION";
                return new MutationPlan(
                    investigation,
                    [new MutationEvent("INVESTIGATION_COMPLETED",
                        "Consultas mock concluídas.",
                        "backoffice.investigation.completed.v1")]);
            },
            cancellationToken);
    }

    public Task<ServiceResult> CreateRecommendationAsync(
        ApiRequestContext context,
        Guid caseId,
        CreateRecommendationRequest request,
        CancellationToken cancellationToken)
    {
        return MutateAsync(
            context, caseId, "recommendation.create", request, request.CaseVersion,
            StatusCodes.Status201Created,
            aggregate => new
            {
                case_version = aggregate.CaseVersion,
                evidence_references = aggregate.Evidence.Select(item => item.EvidenceId).ToArray()
            },
            (aggregate, nextVersion) =>
            {
                EnsureState(aggregate, "UNDER_INVESTIGATION");
                if (aggregate.Investigation is null
                    || aggregate.Investigation.InvestigationId != request.InvestigationId
                    || aggregate.Investigation.Status != "COMPLETED")
                {
                    throw new ApiException(StatusCodes.Status422UnprocessableEntity,
                        "investigation-required", "Investigação concluída e compatível é obrigatória.");
                }

                var recommendation = new RecommendationRecord
                {
                    RecommendationId = Guid.NewGuid(),
                    CaseId = aggregate.CaseId,
                    CaseVersion = nextVersion,
                    RecommendationVersion = (aggregate.Recommendation?.RecommendationVersion ?? 0) + 1,
                    Outcome = "APPROVE",
                    Confidence = 0.93,
                    Rationale = "Evidências sintéticas e findings mock suportam aprovação assistida.",
                    EvidenceReferences = aggregate.Evidence.Select(item => item.EvidenceId).ToList(),
                    RuleReferences = ["BR-008", "BR-009"],
                    CreatedBy = context.Subject.Id,
                    CreatedAt = DateTimeOffset.UtcNow
                };

                aggregate.Recommendation = recommendation;
                aggregate.State = "AWAITING_APPROVAL";
                return new MutationPlan(
                    recommendation,
                    [
                        new MutationEvent("DECISION_PROPOSED", recommendation.Rationale,
                            "backoffice.decision.proposed.v1"),
                        new MutationEvent("APPROVAL_REQUESTED", null,
                            "backoffice.approval.requested.v1")
                    ]);
            },
            cancellationToken);
    }

    public Task<ServiceResult> DecideApprovalAsync(
        ApiRequestContext context,
        Guid caseId,
        ApprovalDecisionRequest request,
        CancellationToken cancellationToken)
    {
        if (request.Decision is not ("APPROVE" or "REJECT" or "REQUEST_MORE_EVIDENCE")
            || string.IsNullOrWhiteSpace(request.Reason))
        {
            throw new ApiException(StatusCodes.Status400BadRequest,
                "invalid-approval", "Decisão e motivo válidos são obrigatórios.");
        }

        return MutateAsync(
            context, caseId, "approval.decide", request, request.CaseVersion,
            StatusCodes.Status201Created,
            aggregate =>
            {
                var recommendation = aggregate.Recommendation;
                return new
                {
                    case_version = aggregate.CaseVersion,
                    recommendation_actor_id = recommendation?.CreatedBy ?? "",
                    recommendation_version = recommendation?.RecommendationVersion ?? 0,
                    approved_recommendation_version = request.RecommendationVersion,
                    authority_limit = context.Subject.AuthorityLimit,
                    amount = aggregate.DisputedAmount.AsDecimal()
                };
            },
            (aggregate, _) =>
            {
                EnsureState(aggregate, "AWAITING_APPROVAL");
                var recommendation = aggregate.Recommendation
                    ?? throw new ApiException(StatusCodes.Status422UnprocessableEntity,
                        "recommendation-required", "Recomendação obrigatória.");

                if (recommendation.RecommendationId != request.RecommendationId
                    || recommendation.RecommendationVersion != request.RecommendationVersion)
                {
                    throw new ApiException(StatusCodes.Status409Conflict,
                        "recommendation-version-conflict",
                        "A recomendação informada não é a versão vigente.");
                }

                var status = request.Decision switch
                {
                    "APPROVE" => "APPROVED",
                    "REJECT" => "REJECTED",
                    _ => "MORE_EVIDENCE_REQUIRED"
                };

                var approval = new ApprovalRecord
                {
                    ApprovalId = Guid.NewGuid(),
                    CaseId = aggregate.CaseId,
                    RecommendationId = recommendation.RecommendationId,
                    RecommendationVersion = recommendation.RecommendationVersion,
                    Status = status,
                    DecidedBy = context.Subject.Id,
                    Reason = request.Reason,
                    DecidedAt = DateTimeOffset.UtcNow,
                    ExpiresAt = DateTimeOffset.UtcNow.AddHours(24)
                };

                aggregate.Approval = approval;
                aggregate.State = status switch
                {
                    "APPROVED" => "APPROVED",
                    "REJECTED" => "REJECTED",
                    _ => "MORE_EVIDENCE_REQUIRED"
                };

                var eventType = status == "APPROVED"
                    ? "backoffice.decision.approved.v1"
                    : "backoffice.decision.rejected.v1";

                return new MutationPlan(
                    approval,
                    [new MutationEvent($"DECISION_{status}", request.Reason, eventType)]);
            },
            cancellationToken);
    }

}
