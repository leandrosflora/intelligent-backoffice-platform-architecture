using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace IntelligentBackoffice.Api;

public sealed class DevJwtValidator
{
    private readonly byte[] _secret;
    private readonly string _issuer;
    private readonly string _audience;

    public DevJwtValidator(IConfiguration configuration)
    {
        var secret = configuration["DemoJwt:Secret"]
            ?? throw new InvalidOperationException("DemoJwt:Secret não configurado.");

        if (Encoding.UTF8.GetByteCount(secret) < 32)
        {
            throw new InvalidOperationException("DemoJwt:Secret deve possuir ao menos 32 bytes.");
        }

        _secret = Encoding.UTF8.GetBytes(secret);
        _issuer = configuration["DemoJwt:Issuer"] ?? "intelligent-backoffice-demo";
        _audience = configuration["DemoJwt:Audience"] ?? "backoffice-api";
    }

    public ApiSubject Validate(string authorizationHeader)
    {
        const string prefix = "Bearer ";
        if (string.IsNullOrWhiteSpace(authorizationHeader)
            || !authorizationHeader.StartsWith(prefix, StringComparison.OrdinalIgnoreCase))
        {
            throw new ApiException(StatusCodes.Status401Unauthorized, "missing-token",
                "Bearer token obrigatório.");
        }

        var token = authorizationHeader[prefix.Length..].Trim();
        var parts = token.Split('.');
        if (parts.Length != 3)
        {
            throw new ApiException(StatusCodes.Status401Unauthorized, "invalid-token",
                "JWT inválido.");
        }

        var signingInput = Encoding.ASCII.GetBytes($"{parts[0]}.{parts[1]}");
        var providedSignature = Base64UrlDecode(parts[2]);
        var expectedSignature = HMACSHA256.HashData(_secret, signingInput);

        if (!CryptographicOperations.FixedTimeEquals(providedSignature, expectedSignature))
        {
            throw new ApiException(StatusCodes.Status401Unauthorized, "invalid-signature",
                "Assinatura JWT inválida.");
        }

        using var header = JsonDocument.Parse(Base64UrlDecode(parts[0]));
        if (!header.RootElement.TryGetProperty("alg", out var alg)
            || alg.GetString() != "HS256")
        {
            throw new ApiException(StatusCodes.Status401Unauthorized, "invalid-algorithm",
                "Somente HS256 é aceito no profile local.");
        }

        using var payload = JsonDocument.Parse(Base64UrlDecode(parts[1]));
        var root = payload.RootElement;

        RequireString(root, "iss", out var issuer);
        RequireString(root, "aud", out var audience);
        RequireString(root, "sub", out var subjectId);
        RequireString(root, "actor_type", out var actorType);
        RequireString(root, "tenant_id", out var tenantIdRaw);
        RequireString(root, "purpose", out var purpose);

        if (!string.Equals(issuer, _issuer, StringComparison.Ordinal)
            || !string.Equals(audience, _audience, StringComparison.Ordinal))
        {
            throw new ApiException(StatusCodes.Status401Unauthorized, "invalid-token-scope",
                "Issuer ou audience inválidos.");
        }

        if (!Guid.TryParse(tenantIdRaw, out var tenantId))
        {
            throw new ApiException(StatusCodes.Status401Unauthorized, "invalid-tenant-claim",
                "Claim tenant_id inválida.");
        }

        if (actorType is not ("HUMAN" or "WORKLOAD"))
        {
            throw new ApiException(StatusCodes.Status401Unauthorized, "invalid-actor-type",
                "Claim actor_type inválida.");
        }

        if (!root.TryGetProperty("roles", out var rolesElement)
            || rolesElement.ValueKind != JsonValueKind.Array)
        {
            throw new ApiException(StatusCodes.Status401Unauthorized, "missing-roles",
                "Claim roles obrigatória.");
        }

        var roles = rolesElement.EnumerateArray()
            .Where(item => item.ValueKind == JsonValueKind.String)
            .Select(item => item.GetString()!)
            .Where(item => !string.IsNullOrWhiteSpace(item))
            .Distinct(StringComparer.Ordinal)
            .ToArray();

        if (roles.Length == 0)
        {
            throw new ApiException(StatusCodes.Status401Unauthorized, "missing-roles",
                "Ao menos uma role é obrigatória.");
        }

        if (!root.TryGetProperty("exp", out var expElement)
            || !expElement.TryGetInt64(out var exp)
            || DateTimeOffset.UtcNow.ToUnixTimeSeconds() >= exp)
        {
            throw new ApiException(StatusCodes.Status401Unauthorized, "expired-token",
                "Token expirado ou sem exp.");
        }

        var authorityLimit = 0m;
        if (root.TryGetProperty("authority_limit", out var authorityElement))
        {
            var raw = authorityElement.ValueKind == JsonValueKind.String
                ? authorityElement.GetString()
                : authorityElement.GetRawText();

            decimal.TryParse(raw, System.Globalization.NumberStyles.Number,
                System.Globalization.CultureInfo.InvariantCulture, out authorityLimit);
        }

        return new ApiSubject(subjectId, actorType, tenantId, roles, purpose, authorityLimit);
    }

    private static void RequireString(JsonElement root, string property, out string value)
    {
        if (!root.TryGetProperty(property, out var element)
            || element.ValueKind != JsonValueKind.String
            || string.IsNullOrWhiteSpace(element.GetString()))
        {
            throw new ApiException(StatusCodes.Status401Unauthorized, "invalid-token",
                $"Claim {property} obrigatória.");
        }

        value = element.GetString()!;
    }

    private static byte[] Base64UrlDecode(string value)
    {
        var normalized = value.Replace('-', '+').Replace('_', '/');
        normalized += (normalized.Length % 4) switch
        {
            2 => "==",
            3 => "=",
            _ => ""
        };

        try
        {
            return Convert.FromBase64String(normalized);
        }
        catch (FormatException ex)
        {
            throw new ApiException(StatusCodes.Status401Unauthorized, "invalid-token",
                $"JWT inválido: {ex.Message}");
        }
    }
}
