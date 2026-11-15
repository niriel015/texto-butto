from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
@receiver(pre_save,sender=get_user_model())
def only_one_owner(sender,instance,**kwargs):
 if instance.is_superuser and sender.objects.filter(is_superuser=True).exclude(pk=instance.pk).exists():
  raise ValidationError('A Hyper Store permite somente um superusuário.')
