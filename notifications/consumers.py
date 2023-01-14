import json
from urllib import request
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from accounts.models import User
from accounts.utils import get_model, required_data
from batch.models import Batch
from institute.models import Institute
from .models import ActiveUser
from batch.services import has_msg_perm, create_batch_msg, create_msg, has_msg_perm_batch
from .utils import ws_response


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
        data_json = json.loads(text_data)
        event_type = data_json["event_type"]
        data = data_json["data"]
        user_role = await self.get_role()

        if (user_role != 'owner'):
            ws_resp = ws_response(
                "", {}, "You are not authorized to send notification.", 401)
            await self.send(ws_resp)

        ws_resp = ws_response(event_type, data, "Notification Sent.")
        await self.channel_layer.group_send(self.group_name, ws_resp)

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
                if user in batch.students.all():
                    return True

                return False
            return False
        else:
            return False

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        text_data = json.loads(text_data)
        event_type = text_data["event_type"]
        if (event_type == "batch.message"):
            await self.channel_layer.group_send(self.group_name, ws_response(event_type, data=text_data))

    async def batch_message(self, data):
        payload = data["data"]
        return await self.send(payload)


class UserToUserRealTime(AsyncJsonWebsocketConsumer):

    async def connect(self):

        self.user = self.scope["user"]
        # Adding User to Channel
        await self.remove_user()
        await self.add_user()
        await self.accept()

    async def disconnect(self, code):
        await self.remove_user()
        await self.close(code=code)

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        data = json.loads(text_data)
        receiver_mobile = data["mobile"]
        event_type = data['event_type']
        data = data["payload"]

        # Get Activate User Channel Name
        channel_name, receiver_user = await self.get_user_channel(receiver_mobile)

        if receiver_user:
            has_perm = await database_sync_to_async(has_msg_perm)(self.user, receiver_user)
            if (has_perm):
                if (channel_name):
                    ws_resp = ws_response(event_type, data, "Msg Sent")
                    return await self.channel_layer.send(channel_name, ws_resp)
            else:
                ws_resp = ws_response(
                    "", {}, "You do not have permission to send Message.", 300)
                return await self.send(ws_resp)
        else:
            ws_resp = ws_response("", {}, "The User Doesn't exists.", 404)
            return await self.send(ws_resp)

    # @database_sync_to_async
    # def noti_teacher_request_accepted(self, data):
    #     teacher_mobile = data.get("teacher_mobile", None)
    #     batch_code = data.get("batch_code", None)
    #     owner = self.user
    #     data=get_model(User, id=int(teacher_mobile))
    #     if(not data["exist"]):
    #         await self.send()

    @database_sync_to_async
    def get_user_channel(self, mobile):
        to_user = get_model(User, mobile=int(mobile))
        if (not to_user["exist"]):
            return False, False

        to_user = to_user['data']

        receiver_channel = ActiveUser.objects.filter(user__mobile=int(mobile))
        if (receiver_channel.exists()):
            receiver_channel = receiver_channel.first()
        else:
            return False, to_user

        return receiver_channel.channel_name, receiver_channel.user

    async def chat_receive(self, data):
        data = data["payload"]
        await self.send(data)

    @database_sync_to_async
    def add_user(self):
        print("User Added to Channel (ActiveUser)")
        ActiveUser.objects.create(user=self.user,
                                  channel_name=self.channel_name)

    @database_sync_to_async
    def remove_user(self):
        output = ActiveUser.objects.filter(user=self.user).delete()
        print(str(output) + " Removed ")
