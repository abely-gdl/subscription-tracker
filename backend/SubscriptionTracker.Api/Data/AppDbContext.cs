namespace SubscriptionTracker.Api.Data;

using Microsoft.EntityFrameworkCore;
using SubscriptionTracker.Api.Models;

public sealed class AppDbContext(DbContextOptions<AppDbContext> options) : DbContext(options)
{
    public DbSet<Subscription> Subscriptions => Set<Subscription>();

    protected override void OnModelCreating(ModelBuilder mb)
    {
        mb.Entity<Subscription>().Property(s => s.BillingCycle).HasConversion<string>();
        mb.Entity<Subscription>().Property(s => s.Status).HasConversion<string>();
    }
}
