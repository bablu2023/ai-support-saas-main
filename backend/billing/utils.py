from django.db.models import Sum
from billing.models import TokenUsage


def get_monthly_usage(organization):
    return (
        TokenUsage.objects
        .filter(organization=organization)
        .aggregate(total=Sum("total_tokens"))
    )["total"] or 0
