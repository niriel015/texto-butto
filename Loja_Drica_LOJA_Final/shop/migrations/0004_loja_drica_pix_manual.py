from django.db import migrations, models

def initial_categories_and_name(apps, schema_editor):
    Category = apps.get_model('shop', 'Category')
    ShopSettings = apps.get_model('shop', 'ShopSettings')
    entries = [
        ('Vestidos', 'vestidos'), ('Blusas e Croppeds', 'blusas-e-croppeds'),
        ('Conjuntos', 'conjuntos'), ('Calças e Jeans', 'calcas-e-jeans'),
        ('Saias e Shorts', 'saias-e-shorts'), ('Bolsas', 'bolsas'),
        ('Calçados', 'calcados'), ('Acessórios', 'acessorios'),
        ('Bijuterias', 'bijuterias'), ('Beleza', 'beleza'),
        ('Moda Íntima', 'moda-intima'), ('Infantil', 'infantil'),
    ]
    for name, slug in entries:
        if not Category.objects.filter(slug=slug).exists() and not Category.objects.filter(name=name).exists():
            Category.objects.create(name=name, slug=slug)
    ShopSettings.objects.filter(store_name__in=['Hyper Femme', 'HYPER FEMME']).update(store_name='Loja Drica')

class Migration(migrations.Migration):
    dependencies = [('shop', '0003_branding_advertisements_api')]
    operations = [
        migrations.AlterField(model_name='shopsettings',name='store_name',field=models.CharField(default='Loja Drica',max_length=100)),
        migrations.AlterField(model_name='advertisement',name='placement',field=models.CharField(choices=[('hero','Banner principal (carrossel)'),('top','Antes das coleções'),('collections','Depois das coleções'),('products','Depois dos produtos')],default='collections',max_length=20)),
        migrations.AddField(model_name='order',name='accepted_at',field=models.DateTimeField(blank=True,null=True)),
        migrations.AddField(model_name='order',name='payment_method',field=models.CharField(choices=[('mercadopago','Mercado Pago'),('manual_pix','Pix direto com conferência manual')],default='mercadopago',max_length=20)),
        migrations.RunPython(initial_categories_and_name,migrations.RunPython.noop),
    ]
