def create_default_plan(sender, **kwargs):
    from billing.models import Plan
    from organizations.models import Organization

    free_plan, _ = Plan.objects.get_or_create(
        name="Free",
        defaults={
            "monthly_token_limit": 10000,
            "price": 0,
        },
    )

    Organization.objects.filter(plan__isnull=True).update(plan=free_plan)
