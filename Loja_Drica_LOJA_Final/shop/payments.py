import hashlib,hmac,uuid
from decimal import Decimal
from django.conf import settings
import requests
class PaymentError(Exception):pass
BASE='https://api.mercadopago.com/v1/payments'
def headers(idempotency_key=None):
 if not settings.MP_ACCESS_TOKEN:raise PaymentError('Credenciais de pagamento não configuradas')
 h={'Authorization':'Bearer '+settings.MP_ACCESS_TOKEN,'Content-Type':'application/json'}
 if idempotency_key:h['X-Idempotency-Key']=idempotency_key
 return h
def create_pix(order,payer):
 payload={'transaction_amount':float(order.total),'description':'Pedido Hyper '+str(order.pk),'payment_method_id':'pix','external_reference':str(order.pk),'payer':{'email':payer['email'],'first_name':payer['first_name'],'last_name':payer['last_name'],'identification':{'type':'CPF','number':payer['cpf']}},'date_of_expiration':order.expires_at.isoformat()}
 try:
  r=requests.post(BASE,json=payload,headers=headers(str(order.pk)),timeout=20)
  r.raise_for_status();return r.json()
 except (requests.RequestException,ValueError) as e:raise PaymentError('Falha de comunicação com o provedor de pagamentos') from e
def get_payment(payment_id):
 try:
  r=requests.get(BASE+'/'+str(payment_id),headers=headers(),timeout=15)
  r.raise_for_status();return r.json()
 except (requests.RequestException,ValueError) as e:raise PaymentError('Falha ao consultar pagamento no provedor') from e
def valid_signature(signature,request_id,data_id):
 if not(settings.MP_WEBHOOK_SECRET and signature and request_id and data_id):return False
 parts=dict(x.strip().split('=',1) for x in signature.split(',') if '=' in x)
 if not parts.get('ts') or not parts.get('v1'):return False
 manifest=f'id:{str(data_id).lower()};request-id:{request_id};ts:{parts["ts"]};'
 digest=hmac.new(settings.MP_WEBHOOK_SECRET.encode(),manifest.encode(),hashlib.sha256).hexdigest()
 return hmac.compare_digest(digest,parts['v1'])
