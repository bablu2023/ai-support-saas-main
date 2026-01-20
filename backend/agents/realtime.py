from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def push_agent_status(user_id, data: dict):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            "type": "agent_status",
            "data": data,
        },
    )
