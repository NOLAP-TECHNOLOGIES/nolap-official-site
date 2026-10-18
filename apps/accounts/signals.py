from allauth.account.signals import user_signed_up
from django.dispatch import receiver

from .models import Organiser


@receiver(user_signed_up)
def create_organiser_on_signup(request, user, **kwargs):
    Organiser.objects.get_or_create(user=user)
