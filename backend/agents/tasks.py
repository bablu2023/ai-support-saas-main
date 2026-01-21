from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
channel_layer = get_channel_layer()
group_name = f"user_{user.id}"


from celery import shared_task
from django.contrib.auth import get_user_model
from organizations.models import Organization
from agents.executor import run_agent
from agents.workflow_agent import WorkflowAgent

async_to_sync(channel_layer.group_send)(
    group_name,
    {
        "type": "agent_status",
        "data": {
            "status": "running",
            "input": input_text,
        },
    },
)

async_to_sync(channel_layer.group_send)(
    group_name,
    {
        "type": "agent_status",
        "data": {
            "status": "completed",
            "result": result.output,
        },
    },
)





@shared_task(bind=True)
def run_workflow_agent_task(self, org_id, user_id, input_text, resume=False, run_id=None):
    User = get_user_model()
    org = Organization.objects.get(id=org_id)
    user = User.objects.get(id=user_id)

    class DummyRequest:
        organization = org
        user = user

    if resume and run_id:
        from agents.models import AgentRun
        run = AgentRun.objects.get(id=run_id)
    else:
        run = None

    return run_agent(
        agent_class=WorkflowAgent,
        request=DummyRequest(),
        input_text=input_text,
        resume=resume,
        existing_run=run,
    )

