using SubscriptionTracker.Api.Endpoints;

var builder = WebApplication.CreateBuilder(args);

var app = builder.Build();

app.MapGet("/health", () => Results.Ok(new { status = "healthy" }));
app.MapSubscriptionEndpoints();

app.Run();
