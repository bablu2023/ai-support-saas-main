from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
channel_layer = get_channel_layer()
group_name = f"user_{user.id}"

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
