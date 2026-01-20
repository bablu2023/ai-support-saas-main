from organizations.usage import can_consume_tokens, consume_tokens
from agents.realtime import push_agent_status


def run_agent(agent_class, request, input_text):
    org = request.organization
    user = request.user

    estimated_tokens = 500

    # 🔔 queued
    push_agent_status(user.id, {
        "status": "queued",
        "agent": agent_class.name,
    })

    if not can_consume_tokens(org, estimated_tokens):
        push_agent_status(user.id, {
            "status": "failed",
            "reason": "quota_exceeded",
        })
        raise PermissionError("Token quota exceeded")

    # 🔔 running
    push_agent_status(user.id, {
        "status": "running",
        "agent": agent_class.name,
    })

    agent = agent_class(org, user)

    try:
        result = agent.run(input_text)
    except Exception as e:
        push_agent_status(user.id, {
            "status": "failed",
            "error": str(e),
        })
        raise

    # 🔔 token accounting
    consume_tokens(org, result.tokens_used)

    # 🔔 completed
    push_agent_status(user.id, {
        "status": "completed",
        "agent": agent_class.name,
        "tokens_used": result.tokens_used,
        "output": result.output,
    })

    return result
