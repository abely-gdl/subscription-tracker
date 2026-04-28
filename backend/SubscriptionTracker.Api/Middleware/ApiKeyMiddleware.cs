namespace SubscriptionTracker.Api.Middleware;

public sealed class ApiKeyMiddleware(RequestDelegate next, IConfiguration config)
{
    private const string HeaderName = "X-Api-Key";

    public async Task InvokeAsync(HttpContext ctx)
    {
        var expectedKey = config["ApiKey"];
        if (string.IsNullOrEmpty(expectedKey))
        {
            ctx.Response.StatusCode = StatusCodes.Status500InternalServerError;
            await ctx.Response.WriteAsJsonAsync(new { error = "API key not configured" });
            return;
        }

        if (!ctx.Request.Headers.TryGetValue(HeaderName, out var providedKey)
            || providedKey != expectedKey)
        {
            ctx.Response.StatusCode = StatusCodes.Status401Unauthorized;
            await ctx.Response.WriteAsJsonAsync(new { error = "Invalid or missing API key" });
            return;
        }

        await next(ctx);
    }
}

public static class ApiKeyMiddlewareExtensions
{
    public static IApplicationBuilder UseApiKeyAuth(this IApplicationBuilder app)
        => app.UseMiddleware<ApiKeyMiddleware>();
}
