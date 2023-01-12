import json
from urllib import request
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from accounts.models import User
from accounts.utils import get_model
from batch.models import Batch
from institute.models import Institute
from .models import ActiveUser
from batch.services import has_msg_perm


class InstituteNotifications(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]
        self.institute_code = self.scope['url_route']['kwargs'][
            'institute_code']

        self.group_name = 'insitute_' + self.institute_code  # Each Institute
        perm_to_connect = await self.has_perm_to_connect()

        if (perm_to_connect):
            await self.channel_layer.group_add(self.group_name,
                                               self.channel_name)
            await self.accept()
        else:
            self.close()

    async def disconnect(self):
        await self.channel_layer.group_discard(self.group_name,
                                               self.channel_name)

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        text_data_json = json.loads(text_data)
        event_type = text_data_json["event_type"]
        data = text_data_json["data"]
        user_role = await self.get_role()

        if (user_role != 'owner'):
            self.send({
                "success": False,
                "msg": None,
                "error": "You are not owner"
            })

        await self.channel_layer.group_send(self.group_name, {
            "type": event_type,
            "message": ""
        })

    @database_sync_to_async
    def get_role(self):
        return self.user.role

    @database_sync_to_async
    def has_perm_to_connect(self, institute_code):
        institute = get_model(Institute, institute_code=institute_code)
        user_role = self.user.role.lower()
        user = self.user

        if (institute["exist"]):
            institute = institute["data"]
            if (user_role == "owner"):
                if (institute.owner == user):
                    return True
                return False

            elif (user_role == "student"):
                student_exist = Batch.objects.filter(institute=institute,
                                                     students__in=[user
                                                                   ]).exists()

                if (student_exist):
                    return True
                return False

            elif (user_role == "teacher"):
                teacher_exist = Batch.objects.filter(institute=institute,
                                                     teacher=user).exists()

                if (teacher_exist):
                    return True
                return False

            return False
        else:
            return False


class BatchNotifications(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]
        self.batch_code = self.scope['url_route']['kwargs']['batch_code']

        self.group_name = 'batchcode_' + self.batch_code  # Each Institute
        perm_to_connect = await self.has_perm_to_connect(self.batch_code)

        if (perm_to_connect):
            await self.channel_layer.group_add(self.group_name,
                                               self.channel_name)
            await self.accept()
        else:
            self.close()

    @database_sync_to_async
    def has_perm_to_connect(self, batch_code):
        batch = get_model(Batch, batch_code=batch_code)
        user_role = self.user.role.lower()
        user = self.user

        if (batch["exist"]):
            batch = batch["data"]
            if (user_role == "teacher"):
                if (batch.teacher == user):
                    return True
                return False

            elif (user_role == "student"):
                student_exist = Batch.objects.filter(batch_code=batch_code,
                                                     students__in=[user
                                                                   ]).exists()

                if (student_exist):
                    return True
                return False

            return False
        else:
            return False


class UserToUserRealTime(AsyncJsonWebsocketConsumer):

    async def connect(self):

        self.user = self.scope["user"]
        # Adding User to Channel
        await self.add_user()
        await self.accept()

    async def disconnect(self, code):
        await self.remove_user()
        await self.close(code=code)

    def receive(self, text_data=None, bytes_data=None, **kwargs):
        data = json.loads(text_data)
        receiver_mobile = data["mobile"]
        message = data["message"]

        channel_name, receiver_user = self.get_user_channel(receiver_mobile)

        if receiver_user:
            if (has_msg_perm(receiver_user, self.user)):
                if (channel_name):
                    self.channel_layer.send(channel_name, {
                        "type": "chat.receive",
                        "payload": message
                    })
            else:
                return
        else:
            pass

    async def chat_receive(self, data):
        data = data["payload"]
        await self.send(data)

    @database_sync_to_async
    def get_user_channel(self, mobile):
        to_user = get_model(User, id=int(mobile))
        if (not to_user["exist"]):
            return False, False

        to_user = to_user['data']

        receiver_channel = ActiveUser.objects.filter(user__mobile=int(mobile))
        if (receiver_channel.exists()):
            receiver_channel = receiver_channel.first()
        else:
            return False, True

        return receiver_channel.channel_name, receiver_channel.user

    @database_sync_to_async
    def add_user(self):
        self.remove_user()
        ActiveUser.objects.create(user=self.user,
                                  channel_name=self.channel_name)

    @database_sync_to_async
    def remove_user(self):
        ActiveUser.objects.filter(user=self.user).delete()


class TestChannel(AsyncJsonWebsocketConsumer):

    async def connect(self):
        return await self.accept()

    async def disconnect(self, code):
        return await self.close(code)
