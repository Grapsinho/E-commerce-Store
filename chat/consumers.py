import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept the WebSocket connection
        await self.accept()
        # Add the consumer to a group based on chat PK
        self.chat_pk = self.scope['url_route']['kwargs']['chat_pk']
        await self.channel_layer.group_add(
            f"chat_{self.chat_pk}",
            self.channel_name
        )

    async def disconnect(self, close_code):
        # Disconnect from WebSocket
        await self.channel_layer.group_discard(
            f"chat_{self.chat_pk}",
            self.channel_name
        )

    async def receive(self, text_data):
        # Receive a message from the WebSocket
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']
        sender_id = text_data_json['sender_id']

        # Create a new message
        await self.create_message(message_content, sender_id, self.chat_pk)

        # Broadcast the message to the group
        await self.channel_layer.group_send(
            f"chat_{self.chat_pk}",
            {
                'type': 'chat_message',
                'message': message_content,
                'sender_id': sender_id,
            }
        )

    @sync_to_async
    def create_message(self, message_content, sender, chat):
        from .models import Message, Chat
        from users.models import Consumer
        
        # Create a new message in the database
        chat = Chat.objects.get(pk=chat)
        sender = Consumer.objects.get(pk=sender)

        if sender == chat.receiver:
            chat.sender_seen = False
            chat.save()
        else:
            chat.receiver_seen = False
            chat.save()

        Message.objects.create(
            content=message_content,
            chat=chat,
            sender=sender,
        )

    async def chat_message(self, event):
        # Send the message to the WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender_id': event['sender_id'],
        }))
