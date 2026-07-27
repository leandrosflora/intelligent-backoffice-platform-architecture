using System.Text.Json;

namespace IntelligentBackoffice.Api;

public static class ApiRequestContextFactory
{
    public static ApiRequestContext Create(
        HttpContext httpContext,
        DevJwtValidator jwtValidator,
        bool requireIdempotency = false,
        bool requireIfMatch = false)
    {
        var subject = jwtValidator.Validate(
            httpContext.Request.Headers.Authorization.ToString());

        if (!Guid.TryParse(
                httpContext.Request.Headers["X-Tenant-Id"].ToString(),
                out var tenantId))
        {
            throw new ApiException(StatusCodes.Status400BadRequest,
                "tenant-required", "X-Tenant-Id deve ser um UUID.");
        }

        if (tenantId != subject.TenantId)
        {
            throw new ApiException(StatusCodes.Status403Forbidden,
                "tenant-mismatch", "Tenant do header não corresponde ao token.");
        }

        if (!Guid.TryParse(
                httpContext.Request.Headers["X-Correlation-Id"].ToString(),
                out var correlationId))
        {
            throw new ApiException(StatusCodes.Status400BadRequest,
                "correlation-required", "X-Correlation-Id deve ser um UUID.");
        }

        var idempotencyKey = httpContext.Request.Headers["Idempotency-Key"].ToString();
        if (requireIdempotency
            && (idempotencyKey.Length < 8 || idempotencyKey.Length > 128))
        {
            throw new ApiException(StatusCodes.Status400BadRequest,
                "idempotency-key-required",
                "Idempotency-Key deve possuir entre 8 e 128 caracteres.");
        }

        int? expectedVersion = null;
        var ifMatch = httpContext.Request.Headers.IfMatch.ToString().Trim('"');
        if (!string.IsNullOrWhiteSpace(ifMatch))
        {
            if (!int.TryParse(ifMatch, out var parsedVersion) || parsedVersion <= 0)
            {
                throw new ApiException(StatusCodes.Status400BadRequest,
                    "invalid-if-match", "If-Match deve conter uma versão inteira positiva.");
            }

            expectedVersion = parsedVersion;
        }
        else if (requireIfMatch)
        {
            throw new ApiException(StatusCodes.Status400BadRequest,
                "if-match-required", "If-Match obrigatório.");
        }

        return new ApiRequestContext(
            subject,
            tenantId,
            correlationId,
            string.IsNullOrWhiteSpace(idempotencyKey) ? null : idempotencyKey,
            expectedVersion);
    }
}

public static class ApiExecution
{
    public static async Task<IResult> RunAsync(
        HttpContext httpContext,
        Func<Task<ServiceResult>> action)
    {
        try
        {
            var result = await action();

            if (result.CaseVersion.HasValue)
            {
                httpContext.Response.Headers.ETag = $"\"{result.CaseVersion.Value}\"";
            }

            if (!string.IsNullOrWhiteSpace(result.Location))
            {
                httpContext.Response.Headers.Location = result.Location;
            }

            if (result.RawJson is not null)
            {
                return Results.Text(
                    result.RawJson,
                    "application/json",
                    statusCode: result.Replay && result.StatusCode == StatusCodes.Status201Created
                        ? StatusCodes.Status200OK
                        : result.StatusCode);
            }

            return Results.Json(
                result.Body,
                JsonDefaults.Options,
                statusCode: result.StatusCode);
        }
        catch (ApiException exception)
        {
            return Problem(httpContext, exception.StatusCode, exception.Code, exception.Message);
        }
        catch (JsonException exception)
        {
            return Problem(httpContext, StatusCodes.Status400BadRequest,
                "invalid-json", exception.Message);
        }
        catch (Exception exception)
        {
            var logger = httpContext.RequestServices
                .GetRequiredService<ILoggerFactory>()
                .CreateLogger("UnhandledException");
            logger.LogError(exception, "Falha não tratada em {Path}.", httpContext.Request.Path);
            return Problem(httpContext, StatusCodes.Status500InternalServerError,
                "internal-error", "Falha interna no vertical slice.");
        }
    }

    public static IResult Problem(
        HttpContext httpContext,
        int status,
        string code,
        string detail)
    {
        return Results.Json(
            new
            {
                type = $"urn:intelligent-backoffice:problem:{code}",
                title = code,
                status,
                detail,
                instance = httpContext.Request.Path.Value,
                traceId = httpContext.TraceIdentifier
            },
            JsonDefaults.Options,
            contentType: "application/problem+json",
            statusCode: status);
    }
}
