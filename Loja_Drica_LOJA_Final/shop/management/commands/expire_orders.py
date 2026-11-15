from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from shop.models import Order,Product
from shop.payments import get_payment,PaymentError
from shop.views import reconcile
class Command(BaseCommand):
 help='Reconcilia pagamentos e libera reservas vencidas somente após consulta ao provedor.'
 def handle(self,*args,**kwargs):
  for order in Order.objects.filter(status=Order.PENDING,payment_method='mercadopago',expires_at__lt=timezone.now()).select_related('payment')[:500]:
   try:
    payment=order.payment
    remote=get_payment(payment.provider_id)
    reconcile(remote)
    if remote.get('status') not in ('cancelled','rejected','refunded','charged_back'):
     # Pending payments still require safe remote cancellation; do not release stock blindly.
     self.stdout.write(f'Pedido {order.pk} mantido reservado; cobrança não encerrada no provedor')
   except (PaymentError,Order.payment.RelatedObjectDoesNotExist):
    self.stderr.write(f'Pedido {order.pk}: requer reconciliação manual')
