namespace IntelligentBackoffice.Api;

public static class EndpointMappings
{
    public static WebApplication MapBackofficeEndpoints(this WebApplication app)
    {
        app.MapGet("/health", async (
            PostgresStore store,
            OpaAuthorizationClient opa,
            CancellationToken cancellationToken) =>
        {
            var database = await store.PingAsync(cancellationToken);
            var policyDecisionPoint = await opa.IsHealthyAsync(cancellationToken);
            var healthy = database && policyDecisionPoint;

            return Results.Json(
                new
                {
                    status = healthy ? "ok" : "degraded",
                    dependencies = new
                    {
                        postgres = database ? "up" : "down",
                        opa = policyDecisionPoint ? "up" : "down"
                    }
                },
                JsonDefaults.Options,
                statusCode: healthy
                    ? StatusCodes.Status200OK
                    : StatusCodes.Status503ServiceUnavailable);
        }).AllowAnonymous();

        app.MapPost("/v1/cases", async (
            HttpContext httpContext,
            CreateCaseRequest request,
            DevJwtValidator jwtValidator,
            CaseWorkflowService service,
            CancellationToken cancellationToken) =>
            await ApiExecution.RunAsync(httpContext, () =>
                service.CreateCaseAsync(
                    ApiRequestContextFactory.Create(
                        httpContext, jwtValidator, requireIdempotency: true),
                    request,
                    cancellationToken)));

        app.MapGet("/v1/cases/{caseId:guid}", async (
            HttpContext httpContext,
            Guid caseId,
            DevJwtValidator jwtValidator,
            CaseWorkflowService service,
            CancellationToken cancellationToken) =>
            await ApiExecution.RunAsync(httpContext, () =>
                service.GetCaseAsync(
                    ApiRequestContextFactory.Create(httpContext, jwtValidator),
                    caseId,
                    cancellationToken)));

        app.MapPost("/v1/cases/{caseId:guid}/cancel", async (
            HttpContext httpContext,
            Guid caseId,
            CancelCaseRequest request,
            DevJwtValidator jwtValidator,
            CaseWorkflowService service,
            CancellationToken cancellationToken) =>
            await ApiExecution.RunAsync(httpContext, () =>
                service.CancelCaseAsync(
                    ApiRequestContextFactory.Create(
                        httpContext, jwtValidator,
                        requireIdempotency: true,
                        requireIfMatch: true),
                    caseId,
                    request,
                    cancellationToken)));

        app.MapPost("/v1/cases/{caseId:guid}/documents", async (
            HttpContext httpContext,
            Guid caseId,
            RegisterDocumentRequest request,
            DevJwtValidator jwtValidator,
            CaseWorkflowService service,
            CancellationToken cancellationToken) =>
            await ApiExecution.RunAsync(httpContext, () =>
                service.RegisterDocumentAsync(
                    ApiRequestContextFactory.Create(
                        httpContext, jwtValidator,
                        requireIdempotency: true,
                        requireIfMatch: true),
                    caseId,
                    request,
                    cancellationToken)));

        app.MapGet("/v1/cases/{caseId:guid}/documents/{documentId:guid}", async (
            HttpContext httpContext,
            Guid caseId,
            Guid documentId,
            DevJwtValidator jwtValidator,
            CaseWorkflowService service,
            CancellationToken cancellationToken) =>
            await ApiExecution.RunAsync(httpContext, () =>
                service.GetDocumentAsync(
                    ApiRequestContextFactory.Create(httpContext, jwtValidator),
                    caseId,
                    documentId,
                    cancellationToken)));

        app.MapGet("/v1/cases/{caseId:guid}/evidence", async (
            HttpContext httpContext,
            Guid caseId,
            DevJwtValidator jwtValidator,
            CaseWorkflowService service,
            CancellationToken cancellationToken) =>
            await ApiExecution.RunAsync(httpContext, () =>
                service.ListEvidenceAsync(
                    ApiRequestContextFactory.Create(httpContext, jwtValidator),
                    caseId,
                    cancellationToken)));

        app.MapPost("/v1/cases/{caseId:guid}/investigations", async (
            HttpContext httpContext,
            Guid caseId,
            InvestigationRequest request,
            DevJwtValidator jwtValidator,
            CaseWorkflowService service,
            CancellationToken cancellationToken) =>
            await ApiExecution.RunAsync(httpContext, () =>
                service.StartInvestigationAsync(
                    ApiRequestContextFactory.Create(
                        httpContext, jwtValidator,
                        requireIdempotency: true,
                        requireIfMatch: true),
                    caseId,
                    request,
                    cancellationToken)));

        app.MapPost("/v1/cases/{caseId:guid}/recommendations", async (
            HttpContext httpContext,
            Guid caseId,
            CreateRecommendationRequest request,
            DevJwtValidator jwtValidator,
            CaseWorkflowService service,
            CancellationToken cancellationToken) =>
            await ApiExecution.RunAsync(httpContext, () =>
                service.CreateRecommendationAsync(
                    ApiRequestContextFactory.Create(
                        httpContext, jwtValidator,
                        requireIdempotency: true,
                        requireIfMatch: true),
                    caseId,
                    request,
                    cancellationToken)));

        app.MapPost("/v1/cases/{caseId:guid}/approvals", async (
            HttpContext httpContext,
            Guid caseId,
            ApprovalDecisionRequest request,
            DevJwtValidator jwtValidator,
            CaseWorkflowService service,
            CancellationToken cancellationToken) =>
            await ApiExecution.RunAsync(httpContext, () =>
                service.DecideApprovalAsync(
                    ApiRequestContextFactory.Create(
                        httpContext, jwtValidator,
                        requireIdempotency: true,
                        requireIfMatch: true),
                    caseId,
                    request,
                    cancellationToken)));

        app.MapPost("/v1/cases/{caseId:guid}/executions", async (
            HttpContext httpContext,
            Guid caseId,
            ExecutionRequest request,
            DevJwtValidator jwtValidator,
            CaseWorkflowService service,
            CancellationToken cancellationToken) =>
            await ApiExecution.RunAsync(httpContext, () =>
                service.RequestExecutionAsync(
                    ApiRequestContextFactory.Create(
                        httpContext, jwtValidator,
                        requireIdempotency: true,
                        requireIfMatch: true),
                    caseId,
                    request,
                    cancellationToken)));

        app.MapGet("/v1/cases/{caseId:guid}/executions/{executionId:guid}", async (
            HttpContext httpContext,
            Guid caseId,
            Guid executionId,
            DevJwtValidator jwtValidator,
            CaseWorkflowService service,
            CancellationToken cancellationToken) =>
            await ApiExecution.RunAsync(httpContext, () =>
                service.GetExecutionAsync(
                    ApiRequestContextFactory.Create(httpContext, jwtValidator),
                    caseId,
                    executionId,
                    cancellationToken)));

        app.MapPost(
            "/v1/cases/{caseId:guid}/reconciliations/{executionId:guid}/resolve",
            async (
                HttpContext httpContext,
                Guid caseId,
                Guid executionId,
                ReconciliationResolutionRequest request,
                DevJwtValidator jwtValidator,
                CaseWorkflowService service,
                CancellationToken cancellationToken) =>
                await ApiExecution.RunAsync(httpContext, () =>
                    service.ResolveReconciliationAsync(
                        ApiRequestContextFactory.Create(
                            httpContext, jwtValidator,
                            requireIdempotency: true,
                            requireIfMatch: true),
                        caseId,
                        executionId,
                        request,
                        cancellationToken)));

        app.MapGet("/v1/cases/{caseId:guid}/timeline", async (
            HttpContext httpContext,
            Guid caseId,
            DevJwtValidator jwtValidator,
            CaseWorkflowService service,
            CancellationToken cancellationToken) =>
            await ApiExecution.RunAsync(httpContext, () =>
                service.GetTimelineAsync(
                    ApiRequestContextFactory.Create(httpContext, jwtValidator),
                    caseId,
                    cancellationToken)));

        return app;
    }
}
