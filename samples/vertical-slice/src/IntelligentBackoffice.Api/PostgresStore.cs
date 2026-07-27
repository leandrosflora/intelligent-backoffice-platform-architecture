using System.Data;
using System.Text.Json;
using Npgsql;
using NpgsqlTypes;

namespace IntelligentBackoffice.Api;

public sealed partial class PostgresStore : IAsyncDisposable
{
    private readonly NpgsqlDataSource _dataSource;
    private readonly ILogger<PostgresStore> _logger;

    public PostgresStore(IConfiguration configuration, ILogger<PostgresStore> logger)
    {
        var connectionString = configuration.GetConnectionString("Postgres")
            ?? throw new InvalidOperationException("ConnectionStrings:Postgres não configurada.");
        _dataSource = NpgsqlDataSource.Create(connectionString);
        _logger = logger;
    }

    public async Task InitializeAsync(CancellationToken cancellationToken = default)
    {
        const string sql = """
            CREATE TABLE IF NOT EXISTS backoffice_cases (
                case_id uuid PRIMARY KEY,
                tenant_id uuid NOT NULL,
                external_reference text NOT NULL,
                state text NOT NULL,
                version integer NOT NULL CHECK (version > 0),
                aggregate jsonb NOT NULL,
                created_at timestamptz NOT NULL,
                updated_at timestamptz NOT NULL,
                UNIQUE (tenant_id, external_reference)
            );

            CREATE INDEX IF NOT EXISTS ix_backoffice_cases_tenant_state
                ON backoffice_cases (tenant_id, state);

            CREATE TABLE IF NOT EXISTS backoffice_idempotency (
                tenant_id uuid NOT NULL,
                scope text NOT NULL,
                idempotency_key text NOT NULL,
                request_hash text NOT NULL,
                response_status integer NOT NULL,
                response_body jsonb NOT NULL,
                created_at timestamptz NOT NULL,
                PRIMARY KEY (tenant_id, scope, idempotency_key)
            );

            CREATE TABLE IF NOT EXISTS backoffice_timeline (
                entry_id uuid PRIMARY KEY,
                tenant_id uuid NOT NULL,
                case_id uuid NOT NULL,
                case_version integer NOT NULL,
                entry jsonb NOT NULL,
                occurred_at timestamptz NOT NULL
            );

            CREATE INDEX IF NOT EXISTS ix_backoffice_timeline_case
                ON backoffice_timeline (tenant_id, case_id, occurred_at);

            CREATE TABLE IF NOT EXISTS backoffice_outbox (
                event_id uuid PRIMARY KEY,
                tenant_id uuid NOT NULL,
                case_id uuid NOT NULL,
                case_version integer NOT NULL,
                event_type text NOT NULL,
                envelope jsonb NOT NULL,
                occurred_at timestamptz NOT NULL,
                published_at timestamptz NULL
            );

            CREATE INDEX IF NOT EXISTS ix_backoffice_outbox_unpublished
                ON backoffice_outbox (occurred_at)
                WHERE published_at IS NULL;
            """;

        Exception? lastException = null;
        for (var attempt = 1; attempt <= 30; attempt++)
        {
            cancellationToken.ThrowIfCancellationRequested();
            try
            {
                await using var connection = await _dataSource.OpenConnectionAsync(cancellationToken);
                await using var command = new NpgsqlCommand(sql, connection);
                await command.ExecuteNonQueryAsync(cancellationToken);
                _logger.LogInformation("PostgreSQL inicializado.");
                return;
            }
            catch (Exception exception) when (exception is NpgsqlException or TimeoutException)
            {
                lastException = exception;
                _logger.LogWarning("PostgreSQL indisponível na tentativa {Attempt}/30.", attempt);
                await Task.Delay(TimeSpan.FromSeconds(2), cancellationToken);
            }
        }

        throw new InvalidOperationException(
            "Não foi possível inicializar o PostgreSQL após 30 tentativas.", lastException);
    }

    public Task<NpgsqlConnection> OpenConnectionAsync(CancellationToken cancellationToken) =>
        _dataSource.OpenConnectionAsync(cancellationToken).AsTask();

    public async Task<bool> PingAsync(CancellationToken cancellationToken)
    {
        try
        {
            await using var connection = await _dataSource.OpenConnectionAsync(cancellationToken);
            await using var command = new NpgsqlCommand("SELECT 1", connection);
            return Convert.ToInt32(await command.ExecuteScalarAsync(cancellationToken)) == 1;
        }
        catch (NpgsqlException)
        {
            return false;
        }
    }

}
