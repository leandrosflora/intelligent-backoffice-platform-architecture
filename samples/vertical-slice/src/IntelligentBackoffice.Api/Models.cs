using System.Text.Json;

namespace IntelligentBackoffice.Api;

public sealed class Money
{
    public string Currency { get; init; } = "BRL";
    public string Amount { get; init; } = "0.00";

    public decimal AsDecimal()
    {
        if (!decimal.TryParse(Amount, System.Globalization.NumberStyles.Number,
                System.Globalization.CultureInfo.InvariantCulture, out var value))
        {
            throw new ApiException(StatusCodes.Status400BadRequest, "invalid-money",
                "Valor monetário inválido.");
        }

        return value;
    }
}

public sealed class CreateCaseRequest
{
    public string ExternalReference { get; init; } = "";
    public string DisputeType { get; init; } = "";
    public string Channel { get; init; } = "";
    public Money DisputedAmount { get; init; } = new();
    public string? CustomerReference { get; init; }
}

public sealed class CancelCaseRequest
{
    public string Reason { get; init; } = "";
}

public sealed class RegisterDocumentRequest
{
    public string DocumentType { get; init; } = "";
    public string MediaType { get; init; } = "";
    public string Checksum { get; init; } = "";
    public string StorageReference { get; init; } = "";
}

public sealed class InvestigationRequest
{
    public int CaseVersion { get; init; }
    public List<string> RequestedChecks { get; init; } = [];
}

public sealed class CreateRecommendationRequest
{
    public int CaseVersion { get; init; }
    public Guid InvestigationId { get; init; }
}

public sealed class ApprovalDecisionRequest
{
    public int CaseVersion { get; init; }
    public Guid RecommendationId { get; init; }
    public int RecommendationVersion { get; init; }
    public string Decision { get; init; } = "";
    public string Reason { get; init; } = "";
    public List<Guid> EvidenceReferences { get; init; } = [];
}

public sealed class ExecutionRequest
{
    public int CaseVersion { get; init; }
    public Guid ApprovalId { get; init; }
    public int RecommendationVersion { get; init; }
    public string CommandType { get; init; } = "";
    public string CommandHash { get; init; } = "";
    public List<Guid> EvidenceReferences { get; init; } = [];
}

public sealed class ReconciliationResolutionRequest
{
    public int CaseVersion { get; init; }
    public string Resolution { get; init; } = "";
    public string Reason { get; init; } = "";
}

public sealed class CaseView
{
    public Guid CaseId { get; init; }
    public Guid TenantId { get; init; }
    public string ExternalReference { get; init; } = "";
    public string DisputeType { get; init; } = "";
    public string Channel { get; init; } = "";
    public string State { get; init; } = "";
    public int CaseVersion { get; init; }
    public string Priority { get; init; } = "NORMAL";
    public Money DisputedAmount { get; init; } = new();
    public DateTimeOffset CreatedAt { get; init; }
    public DateTimeOffset UpdatedAt { get; init; }
}

public sealed class DocumentRecord
{
    public Guid DocumentId { get; init; }
    public Guid CaseId { get; init; }
    public Guid TenantId { get; init; }
    public string DocumentType { get; init; } = "";
    public string Status { get; set; } = "RECEIVED";
    public string MediaType { get; init; } = "";
    public string Checksum { get; init; } = "";
    public int Version { get; init; } = 1;
    public string StorageReference { get; init; } = "";
    public List<string> RejectionReasons { get; init; } = [];
    public DateTimeOffset CreatedAt { get; init; }
}

public sealed class EvidenceRecord
{
    public Guid EvidenceId { get; init; }
    public Guid CaseId { get; init; }
    public Guid TenantId { get; init; }
    public string EvidenceType { get; init; } = "";
    public string SourceType { get; init; } = "";
    public string SourceReference { get; init; } = "";
    public string SourceVersion { get; init; } = "";
    public object? Value { get; init; }
    public double Confidence { get; init; }
    public int? Page { get; init; }
    public string? Position { get; init; }
    public string? Checksum { get; init; }
    public DateTimeOffset CreatedAt { get; init; }
}

public sealed class InvestigationRecord
{
    public Guid InvestigationId { get; init; }
    public Guid CaseId { get; init; }
    public string Status { get; set; } = "PENDING";
    public List<FindingRecord> Findings { get; init; } = [];
    public DateTimeOffset CreatedAt { get; init; }
    public DateTimeOffset? CompletedAt { get; set; }
}

public sealed class FindingRecord
{
    public string Kind { get; init; } = "";
    public string Summary { get; init; } = "";
    public List<Guid> EvidenceReferences { get; init; } = [];
}

public sealed class RecommendationRecord
{
    public Guid RecommendationId { get; init; }
    public Guid CaseId { get; init; }
    public int CaseVersion { get; init; }
    public int RecommendationVersion { get; init; }
    public string Outcome { get; init; } = "";
    public double Confidence { get; init; }
    public string Rationale { get; init; } = "";
    public List<Guid> EvidenceReferences { get; init; } = [];
    public List<string> RuleReferences { get; init; } = [];
    public string CreatedBy { get; init; } = "";
    public DateTimeOffset CreatedAt { get; init; }
}

public sealed class ApprovalRecord
{
    public Guid ApprovalId { get; init; }
    public Guid CaseId { get; init; }
    public Guid RecommendationId { get; init; }
    public int RecommendationVersion { get; init; }
    public string Status { get; init; } = "";
    public string DecidedBy { get; init; } = "";
    public string Reason { get; init; } = "";
    public DateTimeOffset DecidedAt { get; init; }
    public DateTimeOffset? ExpiresAt { get; init; }
}

public sealed class ExecutionRecord
{
    public Guid ExecutionId { get; init; }
    public Guid CaseId { get; init; }
    public string Status { get; set; } = "PENDING";
    public string IdempotencyKey { get; init; } = "";
    public string CommandHash { get; init; } = "";
    public string? ExternalReference { get; set; }
    public DateTimeOffset CreatedAt { get; init; }
    public DateTimeOffset? CompletedAt { get; set; }
}

public sealed class TimelineEntry
{
    public Guid EntryId { get; init; }
    public Guid CaseId { get; init; }
    public int CaseVersion { get; init; }
    public string Type { get; init; } = "";
    public string ActorId { get; init; } = "";
    public string? Reason { get; init; }
    public DateTimeOffset OccurredAt { get; init; }
    public Guid CorrelationId { get; init; }
}

public sealed class CaseAggregate
{
    public Guid CaseId { get; set; }
    public Guid TenantId { get; set; }
    public string ExternalReference { get; set; } = "";
    public string DisputeType { get; set; } = "";
    public string Channel { get; set; } = "";
    public string State { get; set; } = "CREATED";
    public int CaseVersion { get; set; } = 1;
    public string Priority { get; set; } = "NORMAL";
    public Money DisputedAmount { get; set; } = new();
    public string? CustomerReference { get; set; }
    public DateTimeOffset CreatedAt { get; set; }
    public DateTimeOffset UpdatedAt { get; set; }
    public List<DocumentRecord> Documents { get; set; } = [];
    public List<EvidenceRecord> Evidence { get; set; } = [];
    public InvestigationRecord? Investigation { get; set; }
    public RecommendationRecord? Recommendation { get; set; }
    public ApprovalRecord? Approval { get; set; }
    public List<ExecutionRecord> Executions { get; set; } = [];

    public CaseView ToView() => new()
    {
        CaseId = CaseId,
        TenantId = TenantId,
        ExternalReference = ExternalReference,
        DisputeType = DisputeType,
        Channel = Channel,
        State = State,
        CaseVersion = CaseVersion,
        Priority = Priority,
        DisputedAmount = DisputedAmount,
        CreatedAt = CreatedAt,
        UpdatedAt = UpdatedAt
    };
}

public sealed record ApiSubject(
    string Id,
    string Type,
    Guid TenantId,
    IReadOnlyList<string> Roles,
    string Purpose,
    decimal AuthorityLimit);

public sealed record ApiRequestContext(
    ApiSubject Subject,
    Guid TenantId,
    Guid CorrelationId,
    string? IdempotencyKey,
    int? ExpectedVersion);

public sealed record OpaDecision(bool Allow, string Reason, IReadOnlyList<string> Obligations);

public sealed record ServiceResult(
    int StatusCode,
    int? CaseVersion,
    object? Body = null,
    string? RawJson = null,
    bool Replay = false,
    string? Location = null);

public sealed record MutationEvent(string Type, string? Reason = null, string? EventType = null);

public sealed record MutationPlan(object Response, IReadOnlyList<MutationEvent> Events);

public sealed record IdempotencyRecord(
    string RequestHash,
    int ResponseStatus,
    string ResponseBody);

public sealed class ApiException : Exception
{
    public ApiException(int statusCode, string code, string message) : base(message)
    {
        StatusCode = statusCode;
        Code = code;
    }

    public int StatusCode { get; }
    public string Code { get; }
}

public static class JsonDefaults
{
    public static readonly JsonSerializerOptions Options = new(JsonSerializerDefaults.Web)
    {
        PropertyNameCaseInsensitive = true,
        WriteIndented = false
    };
}
