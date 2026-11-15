"""Esquema original da Hyper Store. Compatível com a migração inicial da versão anterior."""
import uuid
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import migrations,models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial=True
    dependencies=[migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations=[
        migrations.CreateModel(name='Category',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('name',models.CharField(max_length=100,unique=True)),
            ('slug',models.SlugField(unique=True)),
        ]),
        migrations.CreateModel(name='ShopSettings',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('store_name',models.CharField(default='Hyper Store',max_length=100)),
            ('support_email',models.EmailField(blank=True,max_length=254)),
        ]),
        migrations.CreateModel(name='Banner',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('title',models.CharField(max_length=180)),
            ('subtitle',models.CharField(blank=True,max_length=240)),
            ('image',models.ImageField(blank=True,upload_to='banners/')),
            ('active',models.BooleanField(default=True)),
        ]),
        migrations.CreateModel(name='Product',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('name',models.CharField(max_length=180)),
            ('slug',models.SlugField(unique=True)),
            ('description',models.TextField(blank=True)),
            ('price',models.DecimalField(decimal_places=2,max_digits=10,validators=[MinValueValidator(0.01)])),
            ('sale_price',models.DecimalField(blank=True,decimal_places=2,max_digits=10,null=True,validators=[MinValueValidator(0.01)])),
            ('stock',models.PositiveIntegerField(default=0)),
            ('image',models.ImageField(blank=True,upload_to='products/')),
            ('active',models.BooleanField(default=True)),
            ('created_at',models.DateTimeField(auto_now_add=True)),
            ('category',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,to='shop.category')),
        ]),
        migrations.CreateModel(name='Order',fields=[
            ('id',models.UUIDField(default=uuid.uuid4,editable=False,primary_key=True,serialize=False)),
            ('status',models.CharField(choices=[('pending','Aguardando pagamento'),('paid','Pago'),('cancelled','Cancelado'),('expired','Expirado')],db_index=True,default='pending',max_length=20)),
            ('total',models.DecimalField(decimal_places=2,max_digits=12)),
            ('created_at',models.DateTimeField(auto_now_add=True)),
            ('updated_at',models.DateTimeField(auto_now=True)),
            ('expires_at',models.DateTimeField(null=True)),
            ('user',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='orders',to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name='OrderItem',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('name',models.CharField(max_length=180)),
            ('unit_price',models.DecimalField(decimal_places=2,max_digits=10)),
            ('quantity',models.PositiveIntegerField()),
            ('order',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='items',to='shop.order')),
            ('product',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,to='shop.product')),
        ]),
        migrations.CreateModel(name='Payment',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('provider_id',models.CharField(max_length=100,unique=True)),
            ('status',models.CharField(max_length=60)),
            ('qr_code',models.TextField(blank=True)),
            ('qr_base64',models.TextField(blank=True)),
            ('amount',models.DecimalField(decimal_places=2,max_digits=12)),
            ('updated_at',models.DateTimeField(auto_now=True)),
            ('order',models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,related_name='payment',to='shop.order')),
        ]),
        migrations.CreateModel(name='AuditLog',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('action',models.CharField(max_length=120)),
            ('details',models.JSONField(blank=True,default=dict)),
            ('created_at',models.DateTimeField(auto_now_add=True)),
            ('actor',models.ForeignKey(null=True,on_delete=django.db.models.deletion.SET_NULL,to=settings.AUTH_USER_MODEL)),
        ]),
    ]
