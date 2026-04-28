namespace SubscriptionTracker.Api.Endpoints;

using System.Collections.Concurrent;
using SubscriptionTracker.Api.Models;

public static class SubscriptionEndpoints
{
    private static readonly ConcurrentDictionary<Guid, Subscription> Store = new();

    public static void MapSubscriptionEndpoints(this WebApplication app)
    {
        var group = app.MapGroup("/subscriptions").WithTags("Subscriptions");

        group.MapGet("/", () => Results.Ok(Store.Values));

        group.MapGet("/{id:guid}", (Guid id) =>
            Store.TryGetValue(id, out var sub) ? Results.Ok(sub) : Results.NotFound());

        group.MapGet("/category/{category}", (string category) =>
            Results.Ok(Store.Values.Where(s =>
                string.Equals(s.Category, category, StringComparison.OrdinalIgnoreCase))));

        group.MapPost("/", (CreateSubscriptionRequest req) =>
        {
            if (string.IsNullOrWhiteSpace(req.Name))
                return Results.BadRequest(new { error = "Name is required" });
            if (req.Cost < 0)
                return Results.BadRequest(new { error = "Cost must be non-negative" });
            if (string.IsNullOrWhiteSpace(req.Category))
                return Results.BadRequest(new { error = "Category is required" });

            var sub = new Subscription
            {
                Name = req.Name,
                Cost = req.Cost,
                BillingCycle = req.BillingCycle,
                Category = req.Category,
                RenewalDate = req.RenewalDate,
                Status = req.Status,
            };
            Store[sub.Id] = sub;
            return Results.Created($"/subscriptions/{sub.Id}", sub);
        });

        group.MapPut("/{id:guid}", (Guid id, UpdateSubscriptionRequest req) =>
        {
            if (!Store.TryGetValue(id, out var sub)) return Results.NotFound();
            if (req.Name is not null) sub.Name = req.Name;
            if (req.Cost is not null) sub.Cost = req.Cost.Value;
            if (req.BillingCycle is not null) sub.BillingCycle = req.BillingCycle.Value;
            if (req.Category is not null) sub.Category = req.Category;
            if (req.RenewalDate is not null) sub.RenewalDate = req.RenewalDate.Value;
            if (req.Status is not null) sub.Status = req.Status.Value;
            return Results.Ok(sub);
        });

        group.MapDelete("/{id:guid}", (Guid id) =>
            Store.TryRemove(id, out _) ? Results.NoContent() : Results.NotFound());
    }
}
