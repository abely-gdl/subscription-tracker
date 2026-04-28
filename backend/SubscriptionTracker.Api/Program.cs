using Microsoft.EntityFrameworkCore;
using SubscriptionTracker.Api.Data;
using SubscriptionTracker.Api.Endpoints;
using SubscriptionTracker.Api.Middleware;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddDbContext<AppDbContext>(opt =>
    opt.UseSqlite(builder.Configuration.GetConnectionString("Default") ?? "Data Source=subscriptions.db"));

var app = builder.Build();

using (var scope = app.Services.CreateScope())
    scope.ServiceProvider.GetRequiredService<AppDbContext>().Database.Migrate();

app.UseWhen(
    ctx => !ctx.Request.Path.StartsWithSegments("/health"),
    b => b.UseApiKeyAuth());

app.MapGet("/health", () => Results.Ok(new { status = "healthy" }));
app.MapSubscriptionEndpoints();

app.Run();
