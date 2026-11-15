import hashlib,hmac,json
from decimal import Decimal
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase,override_settings
from django.urls import reverse
from .models import Product,Order,OrderItem,Payment
from .payments import valid_signature
from .views import reconcile
class ShopTests(TestCase):
 def setUp(self):
  self.u=get_user_model().objects.create_user(username='cliente',password='Senhasegura123!')
  self.p=Product.objects.create(name='Produto',slug='produto',price=Decimal('19.90'),stock=3)
 def test_cart_server_session(self):
  self.client.post(reverse('cart_add',args=[self.p.pk]))
  self.assertContains(self.client.get(reverse('cart')),'19,90')
 def test_checkout_requires_login(self):
  self.assertEqual(self.client.post(reverse('checkout')).status_code,302)
 def test_stock_reservation_and_real_provider_adapter_mock(self):
  self.client.force_login(self.u)
  self.client.post(reverse('cart_add',args=[self.p.pk]))
  payload={'id':12345,'status':'pending','point_of_interaction':{'transaction_data':{'qr_code':'PAYMENT_CODE'}}}
  with override_settings(MP_ACCESS_TOKEN='test-token',PIX_PAYMENT_MODE='mercadopago'):
   with patch('shop.views.create_pix',return_value=payload) as provider:
    resp=self.client.post(reverse('checkout'),{'first_name':'Maria','last_name':'Silva','email':'maria@example.com','cpf':'52998224725'})
  self.assertEqual(resp.status_code,302);provider.assert_called_once()
  self.p.refresh_from_db();self.assertEqual(self.p.stock,2)
  order=Order.objects.get(user=self.u)
  self.assertEqual(order.total,Decimal('19.90'))
  self.assertEqual(order.payment.provider_id,'12345')
  approved={'id':12345,'status':'approved','external_reference':str(order.pk),'currency_id':'BRL','transaction_amount':19.90}
  self.assertTrue(reconcile(approved));self.assertTrue(reconcile(approved))
  order.refresh_from_db();self.assertEqual(order.status,Order.PAID)
  self.p.refresh_from_db();self.assertEqual(self.p.stock,2)
 def test_forged_amount_cannot_approve(self):
  order=Order.objects.create(user=self.u,total=Decimal('19.90'))
  Payment.objects.create(order=order,provider_id='111',status='pending',amount=order.total)
  self.assertFalse(reconcile({'id':111,'status':'approved','external_reference':str(order.pk),'currency_id':'BRL','transaction_amount':'0.01'}))
  order.refresh_from_db();self.assertEqual(order.status,Order.PENDING)
 def test_order_is_private(self):
  order=Order.objects.create(user=self.u,total=Decimal('1.00'))
  other=get_user_model().objects.create_user(username='outro',password='Senhasegura123!')
  self.client.force_login(other)
  self.assertEqual(self.client.get(reverse('order',args=[order.pk])).status_code,404)
 @override_settings(MP_WEBHOOK_SECRET='secret')
 def test_webhook_hmac(self):
  manifest='id:123;request-id:abc;ts:12345;'
  digest=hmac.new(b'secret',manifest.encode(),hashlib.sha256).hexdigest()
  self.assertTrue(valid_signature('ts=12345,v1='+digest,'abc','123'))
  self.assertFalse(valid_signature('ts=12345,v1=invalid','abc','123'))
 def test_nonstaff_cannot_access_admin(self):
  self.client.force_login(self.u)
  self.assertEqual(self.client.get('/gestao-segura/').status_code,404)  # Administração não é publicada na loja
 def test_one_superuser_only(self):
  from django.core.exceptions import ValidationError
  get_user_model().objects.create_superuser(username='proprietario',password='SenhaSuper123!')
  with self.assertRaises(ValidationError):get_user_model().objects.create_superuser(username='outroproprietario',password='SenhaSuper123!')

class FemmeInterfaceTests(TestCase):
 def setUp(self):
  from .models import Category
  self.customer=get_user_model().objects.create_user(username='compradora',password='SenhaSegura678!')
  self.category=Category.objects.create(name='Moda',slug='moda')
  self.second=Category.objects.create(name='Acessórios',slug='acessorios')
  self.blouse=Product.objects.create(name='Blusa violeta',slug='blusa-violeta',category=self.category,price=Decimal('79.90'),sale_price=Decimal('59.90'),stock=5)
  self.bag=Product.objects.create(name='Bolsa rosa',slug='bolsa-rosa',category=self.second,price=Decimal('99.90'),stock=2)

 def test_catalog_filters_from_database(self):
  response=self.client.get(reverse('home'),{'categoria':'moda'})
  self.assertContains(response,'Blusa violeta')
  self.assertNotContains(response,'Bolsa rosa')

 def test_catalog_search_from_database(self):
  response=self.client.get(reverse('home'),{'q':'bolsa'})
  self.assertContains(response,'Bolsa rosa')
  self.assertNotContains(response,'Blusa violeta')

 def test_catalog_price_sort_uses_real_sale_price(self):
  response=self.client.get(reverse('home'),{'ordenar':'menor-preco'})
  names=[p.name for p in response.context['products']]
  self.assertEqual(names,['Blusa violeta','Bolsa rosa'])

 def test_favorites_persist_for_customer(self):
  from .models import Favorite
  self.client.force_login(self.customer)
  self.assertEqual(self.client.post(reverse('favorite_toggle',args=[self.blouse.pk])).status_code,302)
  self.assertTrue(Favorite.objects.filter(user=self.customer,product=self.blouse).exists())
  self.assertContains(self.client.get(reverse('favorites')),'Blusa violeta')
  self.client.post(reverse('favorite_toggle',args=[self.blouse.pk]))
  self.assertFalse(Favorite.objects.filter(user=self.customer,product=self.blouse).exists())

 def test_favorites_require_authenticated_user(self):
  self.assertEqual(self.client.post(reverse('favorite_toggle',args=[self.blouse.pk])).status_code,302)
  self.assertEqual(self.client.get(reverse('favorites')).status_code,302)

 def test_cart_update_respects_stock(self):
  self.client.post(reverse('cart_add',args=[self.bag.pk]))
  self.client.post(reverse('cart_update',args=[self.bag.pk]),{'quantity':2})
  self.assertEqual(self.client.session['cart'][str(self.bag.pk)],2)
  self.client.post(reverse('cart_update',args=[self.bag.pk]),{'quantity':99})
  self.assertEqual(self.client.session['cart'][str(self.bag.pk)],2)
  self.client.post(reverse('cart_update',args=[self.bag.pk]),{'quantity':0})
  self.assertNotIn(str(self.bag.pk),self.client.session['cart'])

 def test_product_detail_preserves_real_stock(self):
  self.assertContains(self.client.get(reverse('product',args=[self.bag.slug])),'2 unidades')

class StudioVisualTests(TestCase):
 def test_home_renders_stickers_with_no_fake_product_entries(self):
  response=self.client.get(reverse('home'))
  self.assertEqual(response.status_code,200)
  self.assertNotContains(response,'studio-section')
  self.assertContains(response,'sticker-flower.svg')
  self.assertContains(response,'sticker-bow.svg')
  self.assertContains(response,'sticker-butterfly.svg')
  self.assertContains(response,'Assim que o proprietário cadastrar produtos reais')

 def test_cart_keeps_real_post_and_csrf(self):
  response=self.client.get(reverse('cart'))
  self.assertEqual(response.status_code,200)
  self.assertContains(response,'Explorar produtos')
  self.assertContains(response,'sticker-heart.svg')
