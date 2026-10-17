from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('shop', '0002_product_taste_packaging_favorite')]
    operations = [
        migrations.AddField(model_name='product', name='available_tastes', field=models.TextField(default='Курица и рис, Нежная говядина, Дикий лосось', verbose_name='Доступные вкусы')),
        migrations.AddField(model_name='product', name='available_packagings', field=models.TextField(default='400 г, 1.5 кг, 3 кг, 10 кг', verbose_name='Доступные фасовки')),
    ]
