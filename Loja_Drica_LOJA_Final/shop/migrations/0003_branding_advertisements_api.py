from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
import django.utils.timezone
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ('shop', '0002_favorite'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.AddField('shopsettings','logo',models.ImageField(blank=True,upload_to='branding/')),
        migrations.AddField('shopsettings','primary_color',models.CharField(max_length=7,default='#A25B7C',validators=[django.core.validators.RegexValidator(r'^#[0-9a-fA-F]{6}$','Use uma cor hexadecimal com 6 dígitos, como #9A5A87.') ])),
        migrations.AddField('shopsettings','secondary_color',models.CharField(max_length=7,default='#71385B',validators=[django.core.validators.RegexValidator(r'^#[0-9a-fA-F]{6}$','Use uma cor hexadecimal com 6 dígitos, como #9A5A87.') ])),
        migrations.AddField('shopsettings','background_color',models.CharField(max_length=7,default='#FCFAF8',validators=[django.core.validators.RegexValidator(r'^#[0-9a-fA-F]{6}$','Use uma cor hexadecimal com 6 dígitos, como #9A5A87.') ])),
        migrations.AddField('shopsettings','text_color',models.CharField(max_length=7,default='#2D2230',validators=[django.core.validators.RegexValidator(r'^#[0-9a-fA-F]{6}$','Use uma cor hexadecimal com 6 dígitos, como #9A5A87.') ])),
        migrations.AddField('shopsettings','headline',models.CharField(max_length=120,default='Seu estilo. Suas regras. Sua essência.')),
        migrations.AddField('shopsettings','headline_subtitle',models.CharField(max_length=300,default='Descubra peças escolhidas para você.')),
        migrations.AddField('shopsettings','tagline',models.CharField(max_length=90,default='BOUTIQUE FEMININA')),
        migrations.AddField('shopsettings','footer_description',models.CharField(max_length=250,blank=True)),
        migrations.AddField('shopsettings','announcement_enabled',models.BooleanField(default=True)),
        migrations.AddField('shopsettings','announcement_text',models.CharField(max_length=180,default='SEU ESTILO, SUAS ESCOLHAS')),
        migrations.AddField('shopsettings','animations_enabled',models.BooleanField(default=True)),
        migrations.AddField('shopsettings','updated_at',models.DateTimeField(auto_now=True,default=django.utils.timezone.now),preserve_default=False),
        migrations.CreateModel(name='Advertisement',fields=[
            ('id',models.BigAutoField(primary_key=True,serialize=False)),
            ('title',models.CharField(max_length=180)),
            ('description',models.CharField(max_length=320,blank=True)),
            ('image',models.ImageField(upload_to='ads/',blank=True)),
            ('destination',models.URLField(max_length=500,help_text='Endereço HTTPS válido para o anúncio')),
            ('button_text',models.CharField(max_length=50,default='Conhecer')),
            ('placement',models.CharField(max_length=20,default='collections',choices=[('top','Antes das coleções'),('collections','Depois das coleções'),('products','Depois dos produtos')])),
            ('position',models.PositiveSmallIntegerField(default=0)),
            ('active',models.BooleanField(default=False)),
            ('starts_at',models.DateTimeField(null=True,blank=True)),
            ('ends_at',models.DateTimeField(null=True,blank=True)),
            ('created_at',models.DateTimeField(auto_now_add=True)),
        ],options={'ordering':['position','-created_at']}),
        migrations.CreateModel(name='AppAccessToken',fields=[
            ('id',models.BigAutoField(primary_key=True,serialize=False)),
            ('name',models.CharField(max_length=70)),
            ('token_id',models.UUIDField(default=uuid.uuid4,unique=True,editable=False)),
            ('secret_digest',models.CharField(max_length=64)),
            ('created_at',models.DateTimeField(auto_now_add=True)),
            ('expires_at',models.DateTimeField()),
            ('last_used_at',models.DateTimeField(null=True,blank=True)),
            ('revoked',models.BooleanField(default=False)),
            ('owner',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL)),
        ],options={'ordering':['-created_at']}),
    ]
