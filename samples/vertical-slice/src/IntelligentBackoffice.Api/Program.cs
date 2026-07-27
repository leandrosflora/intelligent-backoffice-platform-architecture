using IntelligentBackoffice.Api;
using System.Text.Json;

var builder = WebApplication.CreateBuilder(args);

builder.Services.ConfigureHttpJsonOptions(options =>
{
    options.SerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.CamelCase;
    options.SerializerOptions.PropertyNameCaseInsensitive = true;
});

builder.Services.AddSingleton<DevJwtValidator>();
builder.Services.AddSingleton<PostgresStore>();
builder.Services.AddSingleton<CaseWorkflowService>();

builder.Services.AddHttpClient<OpaAuthorizationClient>((serviceProvider, client) =>
{
    var configuration = serviceProvider.GetRequiredService<IConfiguration>();
    var baseUrl = configuration["Opa:BaseUrl"]
        ?? throw new InvalidOperationException("Opa:BaseUrl não configurada.");
    client.BaseAddress = new Uri(baseUrl);
    client.Timeout = TimeSpan.FromSeconds(3);
});

var app = builder.Build();

await app.Services.GetRequiredService<PostgresStore>().InitializeAsync();

app.MapBackofficeEndpoints();

app.Run();

public partial class Program { }
