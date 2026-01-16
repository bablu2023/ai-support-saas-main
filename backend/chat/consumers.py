import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from chat.services.retrieval import rag_chat_stream


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # org is injected by JWT middleware
        self.organization = self.scope.get("organization")

        if not self.organization:
            await self.close()
            return

        self.room_group_name = f"org_{self.organization.id}"

        # Join org room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message")

        if not message:
            return

        # Run streaming RAG in sync thread
        chunks = await sync_to_async(
            lambda: list(
                rag_chat_stream(self.organization, "ws_user", message)
            )
        )()

        # Broadcast each chunk ONLY to this org
        for chunk in chunks:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.message",
                    "content": chunk,
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "chunk",
            "content": event["content"],
        }))




        
