import json,re,uuid
from datetime import timedelta
from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.db.models import F,Sum,Count,Q,Case,When,DecimalField
from django.http import HttpResponseBadRequest,JsonResponse,HttpResponseForbidden
from django.shortcuts import get_object_or_404,redirect,render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Advertisement, Product,Order,OrderItem,Payment,Banner,AuditLog,Category,Favorite
from .payments import create_pix,get_payment,valid_signature,PaymentError
from .pix_static import create_static_pix

def valid_cpf(cpf):
 if len(cpf)!=11 or not cpf.isdigit() or len(set(cpf))==1:return False
 for n in (9,10):
  digit=(sum(int(cpf[i])*(n+1-i) for i in range(n))*10)%11
  if digit==10:digit=0
  if digit!=int(cpf[n]):return False
 return True

def home(request):
 q=request.GET.get('q','').strip()[:100]
 category=request.GET.get('categoria','').strip()[:100]
 order=request.GET.get('ordenar','recentes')
 products=Product.objects.filter(active=True).select_related('category')
 if q:products=products.filter(Q(name__icontains=q)|Q(description__icontains=q))
 if category:products=products.filter(category__slug=category)
 products=products.annotate(actual_price=Case(When(sale_price__isnull=False,then=F('sale_price')),default=F('price'),output_field=DecimalField(max_digits=10,decimal_places=2)))
 sort_options={'recentes':'-created_at','menor-preco':'actual_price','maior-preco':'-actual_price','nome':'name'}
 products=products.order_by(sort_options.get(order,'-created_at'),'-pk')
 from django.core.paginator import Paginator
 page=Paginator(products,12).get_page(request.GET.get('pagina'))
 fav_ids=set(Favorite.objects.filter(user=request.user,product__in=page.object_list).values_list('product_id',flat=True)) if request.user.is_authenticated else set()
 banners=Banner.objects.filter(active=True)[:3]
 ads=Advertisement.published()[:24]
 ad_sections={location:[ad for ad in ads if ad.placement == location] for location in ('top','collections','products')}
 hero_ads=[ad for ad in ads if ad.placement == 'hero']
 return render(request,'shop/home.html',{'products':page,'banners':banners,'ad_sections':ad_sections,'hero_ads':hero_ads,'hero_banner':banners[0] if banners else None,'categories':Category.objects.order_by('name')[:24], 'q':q,'selected_category':category,'sort':order,'favorites':fav_ids,'total_results':products.count()})

def product(request,slug):
 item=get_object_or_404(Product.objects.select_related('category'),slug=slug,active=True)
 related=Product.objects.filter(active=True).exclude(pk=item.pk)
 if item.category_id:related=related.filter(category_id=item.category_id)
 is_favorite=request.user.is_authenticated and Favorite.objects.filter(user=request.user,product=item).exists()
 return render(request,'shop/product.html',{'product':item,'related':related.order_by('-created_at')[:4], 'is_favorite':is_favorite})

@login_required
@require_POST
def favorite_toggle(request,pk):
 product=get_object_or_404(Product,pk=pk,active=True)
 favorite,created=Favorite.objects.get_or_create(user=request.user,product=product)
 if not created:favorite.delete();messages.info(request,'Produto removido dos favoritos.')
 else:messages.success(request,'Produto salvo em seus favoritos.')
 if request.POST.get('from')=='favorites':return redirect('favorites')
 next_url=request.POST.get('next','')
 if next_url and url_has_allowed_host_and_scheme(next_url,allowed_hosts={request.get_host()},require_https=request.is_secure()):return redirect(next_url)
 return redirect('product',slug=product.slug)

@login_required
def favorites(request):
 items=Favorite.objects.filter(user=request.user,product__active=True).select_related('product','product__category')
 return render(request,'shop/favorites.html',{'items':items})

def signup(request):
 if request.method=='POST':
  form=UserCreationForm(request.POST)
  if form.is_valid():
   user=form.save();login(request,user);return redirect('home')
 else:form=UserCreationForm()
 return render(request,'shop/form.html',{'form':form,'heading':'Criar conta'})
def cart(request):
 content=request.session.get('cart',{});items=[];total=Decimal('0')
 products=Product.objects.filter(id__in=content.keys(),active=True)
 for p in products:
  try:qty=min(max(int(content.get(str(p.pk),0)),0),99)
  except (TypeError,ValueError):continue
  if not qty:continue
  sub=p.current_price*qty;total+=sub
  items.append({'product':p,'quantity':qty,'subtotal':sub})
 return render(request,'shop/cart.html',{'items':items,'total':total,'manual_pix':settings.PIX_PAYMENT_MODE=='manual_key'})
@require_POST
def cart_add(request,pk):
 p=get_object_or_404(Product,pk=pk,active=True)
 c=request.session.get('cart',{});key=str(pk)
 qty=min(int(c.get(key,0))+1,99)
 if qty>p.stock:messages.error(request,'Estoque insuficiente')
 else:c[key]=qty;request.session['cart']=c;messages.success(request,'Produto adicionado ao carrinho')
 return redirect('cart')
@require_POST
def cart_remove(request,pk):
 c=request.session.get('cart',{});c.pop(str(pk),None);request.session['cart']=c
 return redirect('cart')
@require_POST
def cart_update(request,pk):
 p=get_object_or_404(Product,pk=pk,active=True)
 try:qty=int(request.POST.get('quantity','0'))
 except (TypeError,ValueError):messages.error(request,'Informe uma quantidade válida.');return redirect('cart')
 if qty<0 or qty>99:messages.error(request,'A quantidade deve ser entre 0 e 99.');return redirect('cart')
 if qty>p.stock:messages.error(request,'Não há unidades suficientes em estoque.');return redirect('cart')
 data=request.session.get('cart',{}).copy()
 if qty==0:data.pop(str(pk),None)
 else:data[str(pk)]=qty
 request.session['cart']=data
 messages.success(request,'Carrinho atualizado.')
 return redirect('cart')

@login_required
def checkout(request):
 if request.method!='POST':return redirect('cart')
 c=request.session.get('cart',{})
 if not c:messages.error(request,'Carrinho vazio');return redirect('cart')
 cpf=re.sub(r'\D','',''.join(request.POST.getlist('cpf')))[:11]
 first=request.POST.get('first_name','').strip()[:100]
 last=request.POST.get('last_name','').strip()[:100]
 email=request.POST.get('email','').strip()[:254]
 if (not first or not last or '@' not in email or (settings.PIX_PAYMENT_MODE!='manual_key' and not valid_cpf(cpf))):
  messages.error(request,'Preencha nome, sobrenome e e-mail válidos' + (' e CPF válido' if settings.PIX_PAYMENT_MODE!='manual_key' else ''));return redirect('cart')
 manual_pix=settings.PIX_PAYMENT_MODE=='manual_key'
 if not manual_pix and not settings.MP_ACCESS_TOKEN:
  messages.error(request,'Pagamento Pix ainda não configurado pelo proprietário');return redirect('cart')
 if manual_pix and not settings.PIX_KEY:
  messages.error(request,'Chave Pix não configurada pelo proprietário.');return redirect('cart')
 try:
  with transaction.atomic():
   ids=sorted(int(x) for x in c)
   products={p.pk:p for p in Product.objects.select_for_update().filter(pk__in=ids,active=True)}
   if len(products)!=len(ids):raise ValueError('Há produtos indisponíveis no carrinho')
   total=Decimal('0');lines=[]
   for pk in ids:
    p=products[pk];qty=int(c[str(pk)])
    if qty<=0 or qty>99 or qty>p.stock:raise ValueError('Estoque insuficiente para '+p.name)
    price=p.current_price
    if price<=0:raise ValueError('Preço indisponível')
    total+=price*qty;lines.append((p,qty,price))
   order=Order.objects.create(user=request.user,total=total,payment_method='manual_pix' if manual_pix else 'mercadopago',expires_at=None if manual_pix else timezone.now()+timedelta(minutes=30))
   if manual_pix:
    qr_code,qr_image=create_static_pix(settings.PIX_KEY,total,order.pk,settings.PIX_RECEIVER_NAME,settings.PIX_RECEIVER_CITY)
    Payment.objects.create(order=order,provider_id=f'manual-{order.pk}',status='awaiting_manual_check',amount=total,qr_code=qr_code,qr_base64=qr_image)
   for p,qty,price in lines:
    OrderItem.objects.create(order=order,product=p,name=p.name,unit_price=price,quantity=qty)
    Product.objects.filter(pk=p.pk).update(stock=F('stock')-qty)
 except (ValueError,TypeError) as e:
  messages.error(request,str(e));return redirect('cart')
 if manual_pix:
  request.session['cart']={}
  return redirect('order',pk=order.pk)
 # Cobrança usa ID fixo como chave de idempotência; falhas não deixam pedido sem rastreabilidade.
 try:
  response=create_pix(order,{'cpf':cpf,'email':email,'first_name':first,'last_name':last})
  pay_id=str(response['id']);status=response.get('status','pending')
  data=response.get('point_of_interaction',{}).get('transaction_data',{})
  with transaction.atomic():
   Payment.objects.create(order=order,provider_id=pay_id,status=status,amount=order.total,qr_code=data.get('qr_code',''),qr_base64=data.get('qr_code_base64',''))
 except (PaymentError,KeyError,TypeError,ValueError) as e:
  # Status fica pendente para reconciliação: uma falha de resposta não prova que a cobrança falhou.
  messages.error(request,'Não foi possível obter o Pix. O pedido foi guardado; contate o suporte para verificar a cobrança.')
  return redirect('order',pk=order.pk)
 request.session['cart']={}
 return redirect('order',pk=order.pk)
@login_required
def order_page(request,pk):
 order=get_object_or_404(Order.objects.prefetch_related('items'),pk=pk,user=request.user)
 return render(request,'shop/order.html',{'order':order,'payment':Payment.objects.filter(order=order).first()})
@login_required
def orders(request):return render(request,'shop/orders.html',{'orders':Order.objects.filter(user=request.user).order_by('-created_at')[:100]})

def reconcile(payment_data):
 """Provider is sole payment authority; account, amount, order ID and currency must match."""
 pid=str(payment_data.get('id',''))
 with transaction.atomic():
  payment=Payment.objects.select_for_update().select_related('order').filter(provider_id=pid).first()
  if payment is None:return False
  order=Order.objects.select_for_update().get(pk=payment.order_id)
  if order.payment_method != 'mercadopago':return False
  if str(payment_data.get('external_reference',''))!=str(order.pk):return False
  if str(payment_data.get('currency_id'))!='BRL':return False
  try: amount=Decimal(str(payment_data.get('transaction_amount','')))
  except Exception:return False
  if amount!=order.total:return False
  status=payment_data.get('status','')
  if status=='approved':
   if order.status!=Order.PENDING:return order.status==Order.PAID
   order.status=Order.PAID;order.save(update_fields=['status','updated_at'])
  elif status in ('cancelled','rejected','refunded','charged_back') and order.status==Order.PENDING:
   for item in order.items.select_related('product'):
    Product.objects.filter(pk=item.product_id).update(stock=F('stock')+item.quantity)
   order.status=Order.CANCELLED;order.save(update_fields=['status','updated_at'])
  payment.status=str(status)[:60];payment.save(update_fields=['status','updated_at'])
  return True
@csrf_exempt
@require_POST
def webhook(request):
 try:payload=json.loads(request.body)
 except (ValueError,UnicodeDecodeError):return HttpResponseBadRequest('Invalid JSON')
 if payload.get('type')!='payment':return JsonResponse({'ignored':True})
 data_id=request.GET.get('data.id') or request.GET.get('id')
 body_id=payload.get('data',{}).get('id')
 if not data_id or str(body_id)!=str(data_id):return HttpResponseBadRequest('ID mismatch')
 if not valid_signature(request.headers.get('x-signature',''),request.headers.get('x-request-id',''),data_id):return HttpResponseForbidden('Invalid signature')
 try:reconcile(get_payment(data_id))
 except PaymentError:return JsonResponse({'retry':True},status=503)
 return JsonResponse({'ok':True})
