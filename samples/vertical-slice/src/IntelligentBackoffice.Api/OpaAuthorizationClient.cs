using System.Net.Http.Json;
using System.Text.Json;

namespace IntelligentBackoffice.Api;

public sealed class OpaAuthorizationClient
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<OpaAuthorizationClient> _logger;

    public OpaAuthorizationClient(HttpClient httpClient, ILogger<OpaAuthorizationClient> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
    }

    public async Task<OpaDecision> DecideAsync(
        ApiRequestContext request,
        string action,
        string resourceState,
        object context,
        CancellationToken cancellationToken)
    {
        var payload = new
        {
            input = new
            {
                subject = new
                {
                    id = request.Subject.Id,
                    type = request.Subject.Type,
                    roles = request.Subject.Roles,
                    tenant_id = request.Subject.TenantId
                },
                resource = new
                {
                    tenant_id = request.TenantId,
                    state = resourceState
                },
                action,
                purpose = request.Subject.Purpose,
                correlation_id = request.CorrelationId,
                context
            }
        };

        try
        {
            using var response = await _httpClient.PostAsJsonAsync(
                "/v1/data/intelligent_backoffice/authorization/decision",
                payload,
                JsonDefaults.Options,
                cancellationToken);

            if (!response.IsSuccessStatusCode)
            {
                _logger.LogWarning("OPA respondeu {StatusCode} para {Action}.",
                    response.StatusCode, action);
                return new OpaDecision(false, "pdp-error", []);
            }

            using var document = await JsonDocument.ParseAsync(
                await response.Content.ReadAsStreamAsync(cancellationToken),
                cancellationToken: cancellationToken);

            if (!document.RootElement.TryGetProperty("result", out var result)
                || !result.TryGetProperty("allow", out var allowElement))
            {
                return new OpaDecision(false, "invalid-pdp-response", []);
            }

            var allow = allowElement.GetBoolean();
            var reason = result.TryGetProperty("reason", out var reasonElement)
                ? reasonElement.GetString() ?? "default-deny"
                : "default-deny";

            var obligations = result.TryGetProperty("obligations", out var obligationsElement)
                && obligationsElement.ValueKind == JsonValueKind.Array
                ? obligationsElement.EnumerateArray()
                    .Where(item => item.ValueKind == JsonValueKind.String)
                    .Select(item => item.GetString()!)
                    .ToArray()
                : [];

            return new OpaDecision(allow, reason, obligations);
        }
        catch (Exception exception) when (
            exception is HttpRequestException
            or TaskCanceledException
            or JsonException)
        {
            _logger.LogError(exception, "OPA indisponível para {Action}; aplicando fail-closed.",
                action);
            return new OpaDecision(false, "pdp-unavailable", []);
        }
    }

    public async Task<bool> IsHealthyAsync(CancellationToken cancellationToken)
    {
        try
        {
            using var response = await _httpClient.GetAsync("/health", cancellationToken);
            return response.IsSuccessStatusCode;
        }
        catch (HttpRequestException)
        {
            return false;
        }
    }
}
