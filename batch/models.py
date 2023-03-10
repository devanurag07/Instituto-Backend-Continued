import os
from django.db import models
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
from accounts.models import User
from institute.models import Institute, Subject
# Create your models here.
# Create your models here.


# Class and Subject
CLASS_CHOICES = [
    (str(i), str(i)) for i in range(1, 13)
]


class Batch(models.Model):
    batch_name = models.CharField(max_length=255)
    batch_code = models.CharField(max_length=255, unique=True)

    grade = models.CharField(
        default="1", choices=CLASS_CHOICES, max_length=20)

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    institute = models.ForeignKey(
        Institute, on_delete=models.CASCADE, related_name="batches")

    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="teacher_batches")

    students = models.ManyToManyField(User, related_name="batches", blank=True)
    blacklist_students = models.ManyToManyField(User, blank=True)

    history = HistoricalRecords()


# Approve Requests
class StudentRequest(models.Model):
    batch = models.ForeignKey(
        Batch, related_name="requests", on_delete=models.CASCADE)

    approved = models.BooleanField(default=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE)

    history = HistoricalRecords()

# MSG API

# Personal Conversation


class Message(models.Model):
    message = models.TextField()
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages")
    reciever = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="recieved_messages", blank=True)

    is_reply = models.BooleanField(default=False)
    parent_msg = models.ForeignKey(
        "Message", on_delete=models.CASCADE, related_name="messages", null=True, blank=True)

    is_batch_msg = models.BooleanField(default=False)
    batch = models.ForeignKey(
        Batch, on_delete=models.CASCADE, related_name="messages", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


# Managing The Media
class Image(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="media/images")
    created_at = models.DateTimeField(auto_now_add=True)


class Media(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    file = models.FileField(upload_to="media/images")
    created_at = models.DateTimeField(auto_now_add=True)


class Blocked(models.Model):
    blocked_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blocklist")

    victim = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)


# MSG API -x -x

# Document API
class Document(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, related_name="documents", on_delete=models.CASCADE)
    batch = models.ForeignKey(
        Batch, on_delete=models.CASCADE, related_name="batch_documents")


def get_upload_path(instance, filename):
    batch_code = instance.document.batch.batch_code.split(" ")[0]
    institute_code = instance.document.batch.institute.institute_code.split(" ")[
        0]

    return os.path.join('documents', institute_code, batch_code)


class DocumentFile(models.Model):
    file = models.FileField(upload_to=get_upload_path)
    document = models.ForeignKey(
        Document, related_name="files", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
