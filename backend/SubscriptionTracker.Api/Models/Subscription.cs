namespace SubscriptionTracker.Api.Models;

public enum BillingCycle { Monthly, Annual }
public enum SubscriptionStatus { Active, Paused, Cancelled }

public sealed class Subscription
{
    public Guid Id { get; init; }
    public required string Name { get; set; }
    public decimal Cost { get; set; }
    public BillingCycle BillingCycle { get; set; }
    public required string Category { get; set; }
    public DateOnly RenewalDate { get; set; }
    public SubscriptionStatus Status { get; set; } = SubscriptionStatus.Active;
}

public sealed record CreateSubscriptionRequest(
    string Name,
    decimal Cost,
    BillingCycle BillingCycle,
    string Category,
    DateOnly RenewalDate,
    SubscriptionStatus Status = SubscriptionStatus.Active
);

public sealed record UpdateSubscriptionRequest(
    string? Name,
    decimal? Cost,
    BillingCycle? BillingCycle,
    string? Category,
    DateOnly? RenewalDate,
    SubscriptionStatus? Status
);
