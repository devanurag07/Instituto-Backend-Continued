from django.db import models
from accounts.models import User
from institute.models import Institute
from batch.models import Batch
# Create your models here.


class ActiveUser(models.Model):
    channel_name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='noti_sent')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="noti_received")
    noti_type = models.CharField(max_length=255)
    noti_msg = models.TextField()
    noti_read = models.BooleanField(default=False)
