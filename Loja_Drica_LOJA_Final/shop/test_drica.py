"""Testes de novas regras comerciais da Loja Drica. Necessitam Django + banco de TESTE."""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from shop.models import Advertisement, Product, Order, Payment, ShopSettings
from shop.pix_static import create_static_pix, _crc16
from shop.views import reconcile


class PixCodeTests(TestCase):
    def test_pix_contains_exact_order_amount_phone_and_valid_crc(self):
        payload, picture = create_static_pix('+5511971992138',Decimal('11.90'),'ca962e42-3d61-4a27-b749-f2cb6d60a328','LOJA DRICA','SAO PAULO')
        self.assertIn('540511.90',payload)
        self.assertIn('+5511971992138',payload)
        self.assertEqual(payload[-4:], _crc16(payload[:-4]))
        self.assertTrue(picture)

    def test_other_total_changes_payload(self):
        a,_=create_static_pix('+5511971992138','11.90','123','LOJA DRICA','SAO PAULO')
        b,_=create_static_pix('+5511971992138','19.90','123','LOJA DRICA','SAO PAULO')
        self.assertNotEqual(a,b)
        self.assertIn('540519.90',b)


@override_settings(PIX_PAYMENT_MODE='manual_key',PIX_KEY='+5511971992138',PIX_RECEIVER_NAME='LOJA DRICA',PIX_RECEIVER_CITY='SAO PAULO')
class DirectPixFlowTests(TestCase):
    def setUp(self):
        self.customer = get_user_model().objects.create_user(username='cliente_drica',password='Abc12345678!')
        self.product = Product.objects.create(name='Produto real',slug='produto-real',price=Decimal('11.90'),stock=2)
        self.client.force_login(self.customer)

    def test_order_persists_with_real_amount_and_is_not_paid_automatically(self):
        self.client.post(reverse('cart_add',args=[self.product.pk]))
        response=self.client.post(reverse('checkout'),{'first_name':'Maria','last_name':'Silva','email':'maria@example.com'})
        self.assertEqual(response.status_code,302)
        order=Order.objects.get(user=self.customer)
        self.assertEqual(order.total,Decimal('11.90'))
        self.assertEqual(order.payment_method,'manual_pix')
        self.assertEqual(order.status,'pending')
        self.assertIsNone(order.accepted_at)
        self.assertEqual(order.payment.status,'awaiting_manual_check')
        self.assertIn('540511.90',order.payment.qr_code)
        self.assertContains(self.client.get(reverse('order',args=[order.pk])),'não consegue confirmar o pagamento automaticamente')
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock,1)

    def test_client_cannot_accept_payment_or_order(self):
        order=Order.objects.create(user=self.customer,total=Decimal('11.90'),payment_method='manual_pix')
        Payment.objects.create(order=order,provider_id='manual-'+str(order.pk),status='awaiting_manual_check',amount=order.total)
        self.assertEqual(self.client.post('/api/v1/admin/orders/'+str(order.pk)+'/accept/').status_code,404)
        self.assertFalse(reconcile({'id':'manual-'+str(order.pk),'status':'approved', 'external_reference':str(order.pk), 'currency_id':'BRL','transaction_amount':'11.90'}))
        order.refresh_from_db()
        self.assertEqual(order.status,Order.PENDING)
        self.assertIsNone(order.accepted_at)

    def test_ad_carousel_uses_only_published_ads_from_database(self):
        Advertisement.objects.create(title='Campanha verdadeira',destination='https://example.org/real',placement='hero',active=True)
        Advertisement.objects.create(title='Campanha privada',destination='https://example.org/private',placement='hero',active=False)
        home=self.client.get(reverse('home'))
        self.assertContains(home,'Campanha verdadeira')
        self.assertNotContains(home,'Campanha privada')
        self.assertContains(home,'drica-hero-carousel')
        self.assertNotContains(home,'Detalhes que fazem')
