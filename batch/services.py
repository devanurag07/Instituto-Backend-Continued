
from re import M
from tokenize import Triple
from accounts.utils import get_model
from batch.models import Batch, Blocked, Message
from accounts.models import User
from batch.serializers import MessageSerializer
from institute.serializers import SubjectSerialzier
from accounts.serializers import User
from institute.services import get_insitute
from rest_framework import serializers
from accounts.serializers import UserSerializer
from batch.models import Document
from institute.models import Institute
from channels.db import database_sync_to_async
# Check For Blocked MSGS


def is_blocked(sender, receiver):
    sender_blocked = Blocked.objects.filter(
        blocked_by=receiver, victim=sender).exists()

    if (sender_blocked):
        return {
            "blocked": True,
            "error": "You can't send msg to the user"
        }
    else:
        receiver_blocked = Blocked.objects.filter(
            blocked_by=sender, victim=receiver).exists()

        if (receiver_blocked):
            return {
                "blocked": True,
                "error": "Unblock The User First.."
            }
    return {
        "blocked": False,
    }


def has_msg_perm(sender, receiver):
    sender_role = sender.role.lower()
    receiver_role = receiver.role.lower()
    import pdb
    pdb.set_trace()
    if (sender_role == "student" and receiver_role == "student"):
        return False

    if (sender_role == "teacher" and receiver_role == "teacher"):
        # Set Intersection
        common_institutes = sender.institutes.all() & receiver.institutes.all()
        if (common_institutes.exists()):
            return True
        return False
    elif (sender_role == "teacher" and receiver_role == "owner"):
        sender_institutes = Institute.objects.filter(teachers__in=[sender])
        receiver_institute = Institute.objects.filter(owner=receiver)
        common_institutes = sender_institutes & receiver_institute
        if (common_institutes.exists()):
            return True

    elif (sender_role == "teacher" and receiver_role == "student"):
        sender_batches = Batch.objects.filter(teacher=sender)
        receiver_batches = Batch.objects.filter(students__in=[receiver])
        common_batches = sender_batches & receiver_batches
        if (common_batches.exists()):
            return True
        return False
    elif (sender_role == "owner" and receiver_role == "teacher"):
        receiver_institute = Institute.objects.filter(teachers__in=[receiver])
        sender_institutes = Institute.objects.filter(owner=sender)
        common_institutes = sender_institutes & receiver_institute
        if (common_institutes.exists()):
            return True
        else:
            return False

    elif (sender_role == "owner" and receiver_role == "student"):
        sender_institutes = Institute.objects.filter(owner=sender)
        receiver_institutes = Institute.objects.filter(
            batches__students__in=[receiver])

        common_institutes = sender_institutes & receiver_institutes
        if (common_institutes.exists()):
            return True
        return False

    elif (sender_role == "student" and receiver_role == "owner"):
        receiver_institutes = Institute.objects.filter(owner=receiver)
        sender_institutes = Institute.objects.filter(
            batches__students__in=[sender])

        common_institutes = sender_institutes & receiver_institutes
        if (common_institutes.exists()):
            return True
        return False

    elif (sender_role == "student" and receiver_role == "teacher"):
        receiver_batches = Batch.objects.filter(teacher=receiver)
        sender_batches = Batch.objects.filter(students__in=[sender])
        import pdb
        pdb.set_trace()
        common_batches = sender_batches & receiver_batches
        if (common_batches.exists()):
            return True
        return False

    return False


def create_msg(request, msg, reciever_id):
    user = request.user
    reciever_user = get_model(User, pk=int(reciever_id))
    is_reply = request.data.get("is_reply", None)
    parent_msg_id = request.data.get("parent_msg", None)

    if (not reciever_user['exist']):
        return {
            "success": False,
            "msg": None,
            "error": "There Is No Such User."
        }

    reciever_user = reciever_user["data"]

    user_type = user.role.lower()
    reciever_user_type = reciever_user.role.lower()

    # IF Communication is Std -> Std

    if (not has_msg_perm(user, reciever_user)):
        return {
            "success": False,
            "msg": None,
            "error": "Permission Not Granted..."
        }

    # Checking Blockage
    has_blocked = is_blocked(user, reciever_user)
    if (has_blocked["blocked"]):
        return {
            "success": False,
            "msg": None,
            "error": has_blocked["error"]
        }

    # Creating Msg
    message = Message(message=msg, sender=user, reciever=reciever_user)

    if (is_reply and parent_msg_id):
        parent_msg = get_model(Message, pk=int(parent_msg_id))
        if (parent_msg["exist"]):
            parent_msg = parent_msg["data"]
            message.parent_msg = parent_msg
            message.is_reply = True

            message.save()

    message.save()
    msg_data = MessageSerializer(message, many=False).data

    return {
        "success": True,
        "data": msg_data
    }


# Check Permission Of Sending MSG
def has_msg_perm_batch(batch, user):
    user_type = user.role.lower()

    if (user_type == "owner"):
        if (user == batch.institute.owner):
            True
        return False

    if (user_type == "teacher"):
        if (batch.teacher == user):
            return True
        return False

    if (user_type == "student"):
        if user in batch.students.all():
            if (user not in batch.blacklist_students.all()):
                return True
            return False
        return False
    return False

# Creates MSG for Batc


def create_batch_msg(request, msg, batch_id):
    user = request.user
    batch = get_model(Batch, pk=int(batch_id))
    is_reply = request.data.get("is_reply", None)
    parent_msg_id = request.data.get("parent_msg", None)

    if (not batch['exist']):
        return {
            "success": False,
            "msg": None,
            "error": "There Is No Such Batch."
        }

    batch = batch["data"]

    if not has_msg_perm_batch(batch, user):
        return {
            "success": False,
            "error": "You are not authorized",
            "msg": None
        }

    message = Message(message=msg, sender=user, batch=batch)

    if (is_reply and parent_msg_id):
        parent_msg = get_model(Message, pk=int(parent_msg_id))
        if (parent_msg["exist"]):
            parent_msg = parent_msg["data"]
            message.parent_msg = parent_msg
            message.is_reply = True

            message.save()

    message.save()
    msg_data = MessageSerializer(message, many=False).data

    return {
        "success": True,
        "data": msg_data
    }


# Retrieve MSGS
def get_convs(user):
    sent_msgs_recivers = Message.objects.filter(
        is_batch_msg=False, sender=user).values_list("receiver")
    received_msgs_senders = Message.objects.filter(
        is_batch_msg=False, receiver=user).values_list("sender")


# BatchView
def get_batch_details(batch):

    class MessageSerializer(serializers.ModelSerializer):
        class Meta:
            model = Message
            fields = "__all__"

    class DocumentSerializer(serializers.ModelSerializer):
        class Meta:
            model = Document
            fields = "__all__"

    class BatchSerializer(serializers.ModelSerializer):
        students = UserSerializer(many=True)
        blacklist_students = UserSerializer(many=True)
        messages_list = serializers.SerializerMethodField()
        documents_list = serializers.SerializerMethodField()
        subject = SubjectSerialzier(many=False)
        teacher = UserSerializer(many=False)

        def get_messages_list(self, batch):
            messages = batch.messages.all()
            return MessageSerializer(messages, many=True).data

        def get_documents_list(self, batch):
            documents = batch.batch_documents.all()
            return DocumentSerializer(documents, many=True).data

        class Meta:
            model = Batch
            fields = "__all__"

    return BatchSerializer(batch).data
