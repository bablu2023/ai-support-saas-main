def can_consume_tokens(organization, tokens):
    if not organization or not organization.plan:
        return False

    limit = organization.plan.monthly_token_limit
    used = organization.monthly_tokens_used

    return (used + tokens) <= limit


def consume_tokens(organization, tokens):
    organization.monthly_tokens_used += tokens
    organization.save(update_fields=["monthly_tokens_used"])


def remaining_tokens(organization):
    if not organization or not organization.plan:
        return 0

    return max(
        organization.plan.monthly_token_limit
        - organization.monthly_tokens_used,
        0,
    )
