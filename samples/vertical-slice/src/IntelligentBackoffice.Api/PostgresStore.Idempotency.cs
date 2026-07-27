using System.Text.Json;
using Npgsql;
using NpgsqlTypes;

namespace IntelligentBackoffice.Api;

public sealed partial class PostgresStore
{
    public async Task<IdempotencyRecord?> GetIdempotencyAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction,
        Guid tenantId,
        string scope,
        string key,
        CancellationToken cancellationToken)
    {
        const string sql = """
            SELECT request_hash, response_status, response_body::text
            FROM backoffice_idempotency
            WHERE tenant_id = @tenant_id
              AND scope = @scope
              AND idempotency_key = @idempotency_key
            FOR UPDATE
            """;

        await using var command = new NpgsqlCommand(sql, connection, transaction);
        command.Parameters.AddWithValue("tenant_id", tenantId);
        command.Parameters.AddWithValue("scope", scope);
        command.Parameters.AddWithValue("idempotency_key", key);

        await using var reader = await command.ExecuteReaderAsync(cancellationToken);
        if (!await reader.ReadAsync(cancellationToken))
        {
            return null;
        }

        return new IdempotencyRecord(
            reader.GetString(0),
            reader.GetInt32(1),
            reader.GetString(2));
    }

    public async Task SaveIdempotencyAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction,
        Guid tenantId,
        string scope,
        string key,
        string requestHash,
        int responseStatus,
        string responseBody,
        CancellationToken cancellationToken)
    {
        const string sql = """
            INSERT INTO backoffice_idempotency (
                tenant_id, scope, idempotency_key, request_hash,
                response_status, response_body, created_at)
            VALUES (
                @tenant_id, @scope, @idempotency_key, @request_hash,
                @response_status, @response_body, @created_at)
            """;

        await using var command = new NpgsqlCommand(sql, connection, transaction);
        command.Parameters.AddWithValue("tenant_id", tenantId);
        command.Parameters.AddWithValue("scope", scope);
        command.Parameters.AddWithValue("idempotency_key", key);
        command.Parameters.AddWithValue("request_hash", requestHash);
        command.Parameters.AddWithValue("response_status", responseStatus);
        command.Parameters.Add("response_body", NpgsqlDbType.Jsonb).Value = responseBody;
        command.Parameters.AddWithValue("created_at", DateTimeOffset.UtcNow);
        await command.ExecuteNonQueryAsync(cancellationToken);
    }

}
