from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import Application, TradeInRequest, CarOrder, CreditRequest


@receiver(post_save, sender=TradeInRequest)
@receiver(post_save, sender=CarOrder)
@receiver(post_save, sender=CreditRequest)
def create_application(sender, instance, created, **kwargs):
    if created:
        Application.objects.create(
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id,
            user=instance.user,
            status='pending'
        )
