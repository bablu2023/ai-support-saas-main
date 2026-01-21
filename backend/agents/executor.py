from django.utils.timezone import now

from organizations.usage import can_consume_tokens, consume_tokens
from agents.realtime import push_agent_status
from agents.models import AgentRun


def run_agent(
    agent_class,
    request,
    input_text,
    resume=False,
    existing_run=None,
):
    org = request.organization
    user = request.user

    estimated_tokens = 500

    # 📝 CREATE OR REUSE RUN
    if resume and existing_run:
        run = existing_run
    else:
        run = AgentRun.objects.create(
            organization=org,
            user=user,
            agent_name=agent_class.name,
            input_text=input_text,
            status="queued",
        )

        push_agent_status(user.id, {
            "status": "queued",
            "agent": agent_class.name,
            "run_id": run.id,
        })

    # 🔐 QUOTA CHECK (only on fresh run)
    if not resume:
        if not can_consume_tokens(org, estimated_tokens):
            run.status = "failed"
            run.error = "Token quota exceeded"
            run.finished_at = now()
            run.save(update_fields=["status", "error", "finished_at"])

            push_agent_status(user.id, {
                "status": "failed",
                "run_id": run.id,
                "reason": "quota_exceeded",
            })
            raise PermissionError("Token quota exceeded")

    # ▶️ RUNNING
    run.status = "running"
    run.save(update_fields=["status"])

    push_agent_status(user.id, {
        "status": "running",
        "agent": agent_class.name,
        "run_id": run.id,
        "resume": resume,
    })

    agent = agent_class(
        org,
        user,
        run_obj=run,
    )

    try:
        result = agent.run(input_text, resume=resume)
    except Exception as e:
        run.status = "failed"
        run.error = str(e)
        run.finished_at = now()
        run.save(update_fields=["status", "error", "finished_at"])

        push_agent_status(user.id, {
            "status": "failed",
            "run_id": run.id,
            "error": str(e),
        })
        raise

    # 💳 TOKEN ACCOUNTING (only if completed)
    if result.tokens_used:
        consume_tokens(org, result.tokens_used)

    # ✅ COMPLETED
    run.status = "completed"
    run.tokens_used = result.tokens_used
    run.output = result.output
    run.actions = result.actions
    run.finished_at = now()
    run.save(update_fields=[
        "status",
        "tokens_used",
        "output",
        "actions",
        "finished_at",
    ])

    push_agent_status(user.id, {
        "status": "completed",
        "agent": agent_class.name,
        "run_id": run.id,
        "tokens_used": result.tokens_used,
    })

    return result
