using System.Text.Json;
using Npgsql;
using NpgsqlTypes;

namespace IntelligentBackoffice.Api;

public sealed partial class PostgresStore
{
    public async Task<CaseAggregate?> GetCaseAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction? transaction,
        Guid tenantId,
        Guid caseId,
        bool forUpdate,
        CancellationToken cancellationToken)
    {
        var sql = """
            SELECT aggregate::text
            FROM backoffice_cases
            WHERE tenant_id = @tenant_id AND case_id = @case_id
            """ + (forUpdate ? " FOR UPDATE" : "");

        await using var command = new NpgsqlCommand(sql, connection, transaction);
        command.Parameters.AddWithValue("tenant_id", tenantId);
        command.Parameters.AddWithValue("case_id", caseId);

        var value = await command.ExecuteScalarAsync(cancellationToken);
        return value is string json
            ? JsonSerializer.Deserialize<CaseAggregate>(json, JsonDefaults.Options)
            : null;
    }

    public async Task<CaseAggregate?> GetCaseByExternalReferenceAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction,
        Guid tenantId,
        string externalReference,
        CancellationToken cancellationToken)
    {
        const string sql = """
            SELECT aggregate::text
            FROM backoffice_cases
            WHERE tenant_id = @tenant_id AND external_reference = @external_reference
            FOR UPDATE
            """;

        await using var command = new NpgsqlCommand(sql, connection, transaction);
        command.Parameters.AddWithValue("tenant_id", tenantId);
        command.Parameters.AddWithValue("external_reference", externalReference);

        var value = await command.ExecuteScalarAsync(cancellationToken);
        return value is string json
            ? JsonSerializer.Deserialize<CaseAggregate>(json, JsonDefaults.Options)
            : null;
    }

    public async Task InsertCaseAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction,
        CaseAggregate aggregate,
        CancellationToken cancellationToken)
    {
        const string sql = """
            INSERT INTO backoffice_cases (
                case_id, tenant_id, external_reference, state, version,
                aggregate, created_at, updated_at)
            VALUES (
                @case_id, @tenant_id, @external_reference, @state, @version,
                @aggregate, @created_at, @updated_at)
            """;

        await using var command = new NpgsqlCommand(sql, connection, transaction);
        command.Parameters.AddWithValue("case_id", aggregate.CaseId);
        command.Parameters.AddWithValue("tenant_id", aggregate.TenantId);
        command.Parameters.AddWithValue("external_reference", aggregate.ExternalReference);
        command.Parameters.AddWithValue("state", aggregate.State);
        command.Parameters.AddWithValue("version", aggregate.CaseVersion);
        command.Parameters.Add("aggregate", NpgsqlDbType.Jsonb).Value =
            JsonSerializer.Serialize(aggregate, JsonDefaults.Options);
        command.Parameters.AddWithValue("created_at", aggregate.CreatedAt);
        command.Parameters.AddWithValue("updated_at", aggregate.UpdatedAt);
        await command.ExecuteNonQueryAsync(cancellationToken);
    }

    public async Task UpdateCaseAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction,
        CaseAggregate aggregate,
        int expectedVersion,
        CancellationToken cancellationToken)
    {
        const string sql = """
            UPDATE backoffice_cases
            SET state = @state,
                version = @new_version,
                aggregate = @aggregate,
                updated_at = @updated_at
            WHERE tenant_id = @tenant_id
              AND case_id = @case_id
              AND version = @expected_version
            """;

        await using var command = new NpgsqlCommand(sql, connection, transaction);
        command.Parameters.AddWithValue("state", aggregate.State);
        command.Parameters.AddWithValue("new_version", aggregate.CaseVersion);
        command.Parameters.Add("aggregate", NpgsqlDbType.Jsonb).Value =
            JsonSerializer.Serialize(aggregate, JsonDefaults.Options);
        command.Parameters.AddWithValue("updated_at", aggregate.UpdatedAt);
        command.Parameters.AddWithValue("tenant_id", aggregate.TenantId);
        command.Parameters.AddWithValue("case_id", aggregate.CaseId);
        command.Parameters.AddWithValue("expected_version", expectedVersion);

        if (await command.ExecuteNonQueryAsync(cancellationToken) != 1)
        {
            throw new ApiException(StatusCodes.Status409Conflict, "case-version-conflict",
                "O caso foi alterado por outro processo.");
        }
    }

}
