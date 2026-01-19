from organizations.usage import can_consume_tokens, consume_tokens

def run_agent(agent_class, request, input_text):
    org = request.organization
    user = request.user

    estimated_tokens = 500

    if not can_consume_tokens(org, estimated_tokens):
        raise PermissionError("Token quota exceeded")

    agent = agent_class(org, user)
    result = agent.run(input_text)

    consume_tokens(org, result.tokens_used)

    return result
