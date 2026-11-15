"""Adiciona favoritos persistentes sem modificar pedidos, preços ou estoque já existentes."""
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies=[migrations.swappable_dependency(settings.AUTH_USER_MODEL),('shop','0001_initial')]
    operations=[
        migrations.CreateModel(name='Favorite',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('created_at',models.DateTimeField(auto_now_add=True)),
            ('product',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='favorites',to='shop.product')),
            ('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='favorites',to=settings.AUTH_USER_MODEL)),
        ],options={'ordering':['-created_at']}),
        migrations.AddConstraint(model_name='favorite',constraint=models.UniqueConstraint(fields=('user','product'),name='unique_favorite_user_product')),
    ]
