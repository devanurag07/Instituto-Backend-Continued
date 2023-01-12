from accounts.models import User
from institute.models import UserProfile
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if (created):
        role = instance.role.lower()
        if (role == "student"):
            UserProfile.objects.create(user=instance)
        elif (role == "owner"):
            UserProfile.objects.create(user=instance)
        else:
            pass
