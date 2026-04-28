namespace SubscriptionTracker.Api.Endpoints;

using Microsoft.EntityFrameworkCore;
using SubscriptionTracker.Api.Data;
using SubscriptionTracker.Api.Models;

public static class SubscriptionEndpoints
{
    public static void MapSubscriptionEndpoints(this WebApplication app)
    {
        var group = app.MapGroup("/subscriptions").WithTags("Subscriptions");

        group.MapGet("/", async (AppDbContext db) =>
            Results.Ok(await db.Subscriptions.ToListAsync()));

        group.MapGet("/{id:guid}", async (Guid id, AppDbContext db) =>
            await db.Subscriptions.FindAsync(id) is { } sub
                ? Results.Ok(sub)
                : Results.NotFound());

        group.MapGet("/category/{category}", async (string category, AppDbContext db) =>
            Results.Ok(await db.Subscriptions
                .Where(s => s.Category.ToLower() == category.ToLower())
                .ToListAsync()));

        group.MapPost("/", async (CreateSubscriptionRequest req, AppDbContext db) =>
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
            db.Subscriptions.Add(sub);
            await db.SaveChangesAsync();
            return Results.Created($"/subscriptions/{sub.Id}", sub);
        });

        group.MapPut("/{id:guid}", async (Guid id, UpdateSubscriptionRequest req, AppDbContext db) =>
        {
            var sub = await db.Subscriptions.FindAsync(id);
            if (sub is null) return Results.NotFound();

            if (req.Name is not null) sub.Name = req.Name;
            if (req.Cost is not null) sub.Cost = req.Cost.Value;
            if (req.BillingCycle is not null) sub.BillingCycle = req.BillingCycle.Value;
            if (req.Category is not null) sub.Category = req.Category;
            if (req.RenewalDate is not null) sub.RenewalDate = req.RenewalDate.Value;
            if (req.Status is not null) sub.Status = req.Status.Value;

            await db.SaveChangesAsync();
            return Results.Ok(sub);
        });

        group.MapDelete("/{id:guid}", async (Guid id, AppDbContext db) =>
        {
            var sub = await db.Subscriptions.FindAsync(id);
            if (sub is null) return Results.NotFound();
            db.Subscriptions.Remove(sub);
            await db.SaveChangesAsync();
            return Results.NoContent();
        });
    }
}
