namespace IntelligentBackoffice.Api;

public sealed partial class CaseWorkflowService
{
    public Task<ServiceResult> RegisterDocumentAsync(
        ApiRequestContext context,
        Guid caseId,
        RegisterDocumentRequest request,
        CancellationToken cancellationToken)
    {
        ValidateDocument(request);

        return MutateAsync(
            context, caseId, "document.register", request, context.ExpectedVersion ?? 0,
            StatusCodes.Status202Accepted,
            aggregate => new { case_version = aggregate.CaseVersion },
            (aggregate, _) =>
            {
                EnsureState(aggregate, "CREATED", "AWAITING_DOCUMENTS", "DOCUMENTS_RECEIVED");
                var now = DateTimeOffset.UtcNow;
                var document = new DocumentRecord
                {
                    DocumentId = Guid.NewGuid(),
                    CaseId = aggregate.CaseId,
                    TenantId = aggregate.TenantId,
                    DocumentType = request.DocumentType,
                    Status = "VALIDATED",
                    MediaType = request.MediaType,
                    Checksum = request.Checksum.ToLowerInvariant(),
                    Version = 1,
                    StorageReference = request.StorageReference,
                    CreatedAt = now
                };

                var evidence = new EvidenceRecord
                {
                    EvidenceId = Guid.NewGuid(),
                    CaseId = aggregate.CaseId,
                    TenantId = aggregate.TenantId,
                    EvidenceType = "EXTRACTED_FIELD",
                    SourceType = "DOCUMENT",
                    SourceReference = document.DocumentId.ToString(),
                    SourceVersion = "1",
                    Value = new { field = "documentValidated", value = true },
                    Confidence = 0.99,
                    Checksum = document.Checksum,
                    CreatedAt = now
                };

                aggregate.Documents.Add(document);
                aggregate.Evidence.Add(evidence);
                aggregate.State = "DOCUMENTS_VALIDATED";

                return new MutationPlan(
                    document,
                    [
                        new MutationEvent("DOCUMENT_RECEIVED", null,
                            "backoffice.document.received.v1"),
                        new MutationEvent("DOCUMENT_VALIDATED",
                            "Document Intelligence mock validou o documento.",
                            "backoffice.document.validated.v1")
                    ]);
            },
            cancellationToken);
    }

    public async Task<ServiceResult> GetDocumentAsync(
        ApiRequestContext context,
        Guid caseId,
        Guid documentId,
        CancellationToken cancellationToken)
    {
        await using var connection = await _store.OpenConnectionAsync(cancellationToken);
        var aggregate = await RequireCaseAsync(
            connection, null, context.TenantId, caseId, false, cancellationToken);
        await AuthorizeAsync(context, "document.read", aggregate.State,
            new { case_version = aggregate.CaseVersion }, cancellationToken);

        var document = aggregate.Documents.SingleOrDefault(item => item.DocumentId == documentId)
            ?? throw new ApiException(StatusCodes.Status404NotFound,
                "document-not-found", "Documento não encontrado.");
        return new ServiceResult(StatusCodes.Status200OK, aggregate.CaseVersion, document);
    }

    public async Task<ServiceResult> ListEvidenceAsync(
        ApiRequestContext context,
        Guid caseId,
        CancellationToken cancellationToken)
    {
        await using var connection = await _store.OpenConnectionAsync(cancellationToken);
        var aggregate = await RequireCaseAsync(
            connection, null, context.TenantId, caseId, false, cancellationToken);
        await AuthorizeAsync(context, "evidence.read", aggregate.State,
            new { case_version = aggregate.CaseVersion }, cancellationToken);
        return new ServiceResult(StatusCodes.Status200OK, aggregate.CaseVersion, aggregate.Evidence);
    }

}
