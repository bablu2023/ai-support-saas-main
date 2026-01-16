from datetime import date

from billing.utils import get_monthly_usage

from django.db.models import Sum
from billing.models import TokenUsage
from billing.utils import get_monthly_usage

class UsageLimitExceeded(Exception):
    pass


def enforce_chat_limit(organization, tokens_used=0):
    plan = organization.plan

    if not plan:
        raise UsageLimitExceeded("No plan assigned to organization")

    month_start = date.today().replace(day=1)

    usage, _ = OrganizationUsage.objects.get_or_create(
        organization=organization,
        month=month_start,
    )

    # Chat limit
    if usage.chats_used >= plan.monthly_chat_limit:
        raise UsageLimitExceeded("Monthly chat limit exceeded")

    # Token limit (if applicable)
    if plan.monthly_token_limit is not None:
        if usage.tokens_used + tokens_used > plan.monthly_token_limit:
            raise UsageLimitExceeded("Monthly token limit exceeded")

    # Increment usage
    usage.chats_used += 1
    usage.tokens_used += tokens_used
    usage.save()

    


class UsageLimitExceeded(Exception):
    pass


def enforce_token_limit(organization, new_tokens: int):
    usage = get_monthly_usage(organization)
    limit = organization.plan.monthly_token_limit

    if usage + new_tokens > limit:
        raise UsageLimitExceeded(
            f"Monthly token limit exceeded ({limit} tokens)"
        )



