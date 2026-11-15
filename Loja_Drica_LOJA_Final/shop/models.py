import uuid
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q
class Category(models.Model):
 name=models.CharField(max_length=100,unique=True)
 slug=models.SlugField(unique=True)
 def __str__(self): return self.name
class Product(models.Model):
 name=models.CharField(max_length=180)
 slug=models.SlugField(unique=True)
 description=models.TextField(blank=True)
 category=models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,blank=True)
 price=models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(0.01)])
 sale_price=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,validators=[MinValueValidator(0.01)])
 stock=models.PositiveIntegerField(default=0)
 image=models.ImageField(upload_to='products/',blank=True)
 active=models.BooleanField(default=True)
 created_at=models.DateTimeField(auto_now_add=True)
 @property
 def current_price(self): return self.sale_price if self.sale_price is not None else self.price
 def __str__(self): return self.name
class Banner(models.Model):
 title=models.CharField(max_length=180)
 subtitle=models.CharField(max_length=240,blank=True)
 image=models.ImageField(upload_to='banners/',blank=True)
 active=models.BooleanField(default=True)
 def __str__(self): return self.title
color_validator = RegexValidator(r'^#[0-9a-fA-F]{6}$', 'Use uma cor hexadecimal com 6 dígitos, como #9A5A87.')

class ShopSettings(models.Model):
 store_name = models.CharField(max_length=100, default='Loja Drica')
 support_email = models.EmailField(blank=True)
 logo = models.ImageField(upload_to='branding/', blank=True)
 primary_color = models.CharField(max_length=7, default='#A25B7C', validators=[color_validator])
 secondary_color = models.CharField(max_length=7, default='#71385B', validators=[color_validator])
 background_color = models.CharField(max_length=7, default='#FCFAF8', validators=[color_validator])
 text_color = models.CharField(max_length=7, default='#2D2230', validators=[color_validator])
 headline = models.CharField(max_length=120, default='Seu estilo. Suas regras. Sua essência.')
 headline_subtitle = models.CharField(max_length=300, default='Descubra peças escolhidas para você.')
 tagline = models.CharField(max_length=90, default='BOUTIQUE FEMININA')
 footer_description = models.CharField(max_length=250, blank=True)
 announcement_enabled = models.BooleanField(default=True)
 announcement_text = models.CharField(max_length=180, default='SEU ESTILO, SUAS ESCOLHAS')
 animations_enabled = models.BooleanField(default=True)
 updated_at = models.DateTimeField(auto_now=True)

 def __str__(self):
  return self.store_name

class Advertisement(models.Model):
    HERO = 'hero'
    ABOVE_COLLECTIONS = 'top'
    BELOW_COLLECTIONS = 'collections'
    AFTER_PRODUCTS = 'products'
    PLACEMENTS = [(HERO, 'Banner principal (carrossel)'), (ABOVE_COLLECTIONS, 'Antes das coleções'),
                  (BELOW_COLLECTIONS, 'Depois das coleções'),
                  (AFTER_PRODUCTS, 'Depois dos produtos')]
    title = models.CharField(max_length=180)
    description = models.CharField(max_length=320, blank=True)
    image = models.ImageField(upload_to='ads/', blank=True)
    destination = models.URLField(max_length=500, help_text='Endereço HTTPS válido para o anúncio')
    button_text = models.CharField(max_length=50, default='Conhecer')
    placement = models.CharField(max_length=20, choices=PLACEMENTS, default=BELOW_COLLECTIONS)
    position = models.PositiveSmallIntegerField(default=0)
    active = models.BooleanField(default=False)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['position', '-created_at']

    def clean(self):
        from urllib.parse import urlsplit
        if self.destination:
            parsed = urlsplit(self.destination)
            if parsed.scheme.lower() != 'https' or not parsed.hostname:
                raise ValidationError({'destination': 'Anúncios exigem um endereço HTTPS válido.'})
        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            raise ValidationError({'ends_at': 'O término deve ocorrer depois do início.'})

    @classmethod
    def published(cls):
        now = timezone.now()
        return cls.objects.filter(active=True).filter(Q(starts_at__isnull=True) | Q(starts_at__lte=now)).filter(
            Q(ends_at__isnull=True) | Q(ends_at__gte=now)).order_by('position', '-created_at')

    def __str__(self):
        return self.title

class AppAccessToken(models.Model):
    """Só guarda digest HMAC de um token de alta entropia, nunca o segredo em texto."""
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=70)
    token_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    secret_digest = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    last_used_at = models.DateTimeField(null=True, blank=True)
    revoked = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

class Order(models.Model):
 PENDING='pending'; PAID='paid'; CANCELLED='cancelled'; EXPIRED='expired'
 STATUS=[(PENDING,'Aguardando pagamento'),(PAID,'Pago'),(CANCELLED,'Cancelado'),(EXPIRED,'Expirado')]
 id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
 user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='orders')
 status=models.CharField(max_length=20,choices=STATUS,default=PENDING,db_index=True)
 total=models.DecimalField(max_digits=12,decimal_places=2)
 payment_method=models.CharField(max_length=20,default='mercadopago',choices=[('mercadopago','Mercado Pago'),('manual_pix','Pix direto com conferência manual')])
 accepted_at=models.DateTimeField(null=True,blank=True)
 created_at=models.DateTimeField(auto_now_add=True)
 updated_at=models.DateTimeField(auto_now=True)
 expires_at=models.DateTimeField(null=True)
 @property
 def customer_status(self):
  if self.status == self.CANCELLED:return 'Cancelado'
  if self.status == self.EXPIRED:return 'Expirado'
  if self.accepted_at:return 'Pedido aceito'
  if self.status == self.PAID:return 'Pagamento confirmado — aguardando aceitação'
  return 'Aguardando pagamento'
 def __str__(self):return str(self.id)
class OrderItem(models.Model):
 order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items')
 product=models.ForeignKey(Product,on_delete=models.PROTECT)
 name=models.CharField(max_length=180)
 unit_price=models.DecimalField(max_digits=10,decimal_places=2)
 quantity=models.PositiveIntegerField()
class Payment(models.Model):
 order=models.OneToOneField(Order,on_delete=models.CASCADE,related_name='payment')
 provider_id=models.CharField(max_length=100,unique=True)
 status=models.CharField(max_length=60)
 qr_code=models.TextField(blank=True)
 qr_base64=models.TextField(blank=True)
 amount=models.DecimalField(max_digits=12,decimal_places=2)
 updated_at=models.DateTimeField(auto_now=True)
class AuditLog(models.Model):
 actor=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,on_delete=models.SET_NULL)
 action=models.CharField(max_length=120)
 details=models.JSONField(default=dict,blank=True)
 created_at=models.DateTimeField(auto_now_add=True)


class Favorite(models.Model):
    """Wishlist persistente por cliente. Não interfere no estoque nem nos pedidos."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'product'], name='unique_favorite_user_product')]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user_id} → {self.product_id}'
