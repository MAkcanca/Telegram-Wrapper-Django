from django.conf import settings
from django.db.models import Model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from telegramwrap import config

from rest_framework.authtoken.models import Token


class TelegramAuthorization(Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=254, unique=True)
    telegram_id = models.CharField(max_length=254, unique=True, null=True, blank=True)
    code = models.IntegerField(null=True, blank=True)
    phone_code_hash = models.CharField(max_length=254, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.phone


class WebhookUrl(Model):
    url = models.CharField(max_length=150)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)