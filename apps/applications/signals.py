from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import AuditLog, Request


@receiver(pre_save, sender=Request)
def request_pre_save(sender, instance: Request, **kwargs):
    if instance.pk:
        try:
            old = Request.objects.get(pk=instance.pk)
            instance._old_status = old.status
        except Request.DoesNotExist:
            instance._old_status = ""
    else:
        instance._old_status = ""


@receiver(post_save, sender=Request)
def request_post_save(sender, instance: Request, created: bool, **kwargs):
    if created:
        AuditLog.objects.create(
            request=instance,
            old_status="",
            new_status=instance.status,
            changed_by=getattr(instance, "_changed_by", None),
        )
        return

    old_status = getattr(instance, "_old_status", "")
    if old_status and old_status != instance.status:
        AuditLog.objects.create(
            request=instance,
            old_status=old_status,
            new_status=instance.status,
            changed_by=getattr(instance, "_changed_by", None),
        )
