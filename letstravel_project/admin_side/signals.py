from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PhoneNumber

@receiver(post_save, sender=User)
def create_phone_number(sender, instance, created, **kwargs):
    if created:
        PhoneNumber.objects.create(user=instance)