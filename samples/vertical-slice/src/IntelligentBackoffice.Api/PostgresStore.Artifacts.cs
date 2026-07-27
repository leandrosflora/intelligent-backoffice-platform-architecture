using System.Text.Json;
using Npgsql;
using NpgsqlTypes;

namespace IntelligentBackoffice.Api;

public sealed partial class PostgresStore
{
    public async Task AppendTimelineAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction,
        Guid tenantId,
        TimelineEntry entry,
        CancellationToken cancellationToken)
    {
        const string sql = """
            INSERT INTO backoffice_timeline (
                entry_id, tenant_id, case_id, case_version, entry, occurred_at)
            VALUES (
                @entry_id, @tenant_id, @case_id, @case_version, @entry, @occurred_at)
            """;

        await using var command = new NpgsqlCommand(sql, connection, transaction);
        command.Parameters.AddWithValue("entry_id", entry.EntryId);
        command.Parameters.AddWithValue("tenant_id", tenantId);
        command.Parameters.AddWithValue("case_id", entry.CaseId);
        command.Parameters.AddWithValue("case_version", entry.CaseVersion);
        command.Parameters.Add("entry", NpgsqlDbType.Jsonb).Value =
            JsonSerializer.Serialize(entry, JsonDefaults.Options);
        command.Parameters.AddWithValue("occurred_at", entry.OccurredAt);
        await command.ExecuteNonQueryAsync(cancellationToken);
    }

    public async Task AppendOutboxAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction,
        ApiRequestContext request,
        CaseAggregate aggregate,
        string eventType,
        CancellationToken cancellationToken)
    {
        var now = DateTimeOffset.UtcNow;
        var eventId = Guid.NewGuid();
        var envelope = new
        {
            eventId,
            eventType,
            eventVersion = 1,
            occurredAt = now,
            tenantId = aggregate.TenantId,
            caseId = aggregate.CaseId,
            caseVersion = aggregate.CaseVersion,
            correlationId = request.CorrelationId,
            causationId = request.CorrelationId,
            producer = "intelligent-backoffice-api",
            dataClassification = "CONFIDENTIAL",
            payload = new
            {
                state = aggregate.State
            }
        };

        const string sql = """
            INSERT INTO backoffice_outbox (
                event_id, tenant_id, case_id, case_version,
                event_type, envelope, occurred_at)
            VALUES (
                @event_id, @tenant_id, @case_id, @case_version,
                @event_type, @envelope, @occurred_at)
            """;

        await using var command = new NpgsqlCommand(sql, connection, transaction);
        command.Parameters.AddWithValue("event_id", eventId);
        command.Parameters.AddWithValue("tenant_id", aggregate.TenantId);
        command.Parameters.AddWithValue("case_id", aggregate.CaseId);
        command.Parameters.AddWithValue("case_version", aggregate.CaseVersion);
        command.Parameters.AddWithValue("event_type", eventType);
        command.Parameters.Add("envelope", NpgsqlDbType.Jsonb).Value =
            JsonSerializer.Serialize(envelope, JsonDefaults.Options);
        command.Parameters.AddWithValue("occurred_at", now);
        await command.ExecuteNonQueryAsync(cancellationToken);
    }

    public async Task<IReadOnlyList<TimelineEntry>> GetTimelineAsync(
        NpgsqlConnection connection,
        Guid tenantId,
        Guid caseId,
        CancellationToken cancellationToken)
    {
        const string sql = """
            SELECT entry::text
            FROM backoffice_timeline
            WHERE tenant_id = @tenant_id AND case_id = @case_id
            ORDER BY occurred_at, entry_id
            """;

        await using var command = new NpgsqlCommand(sql, connection);
        command.Parameters.AddWithValue("tenant_id", tenantId);
        command.Parameters.AddWithValue("case_id", caseId);

        var entries = new List<TimelineEntry>();
        await using var reader = await command.ExecuteReaderAsync(cancellationToken);
        while (await reader.ReadAsync(cancellationToken))
        {
            var entry = JsonSerializer.Deserialize<TimelineEntry>(
                reader.GetString(0), JsonDefaults.Options);
            if (entry is not null)
            {
                entries.Add(entry);
            }
        }

        return entries;
    }

    public async ValueTask DisposeAsync()
    {
        await _dataSource.DisposeAsync();
    }
}
