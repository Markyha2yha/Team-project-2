from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [('shop', '0001_initial'), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.AddField(model_name='product', name='main_taste', field=models.CharField(choices=[('chicken_rice', 'Курица и рис'), ('beef', 'Нежная говядина'), ('salmon', 'Дикий лосось')], default='chicken_rice', max_length=30, verbose_name='Основной вкус')),
        migrations.AddField(model_name='product', name='packaging', field=models.CharField(choices=[('400 г', '400 г'), ('1.5 кг', '1.5 кг'), ('3 кг', '3 кг'), ('10 кг', '10 кг')], default='1.5 кг', max_length=20, verbose_name='Фасовка')),
        migrations.CreateModel(name='Favorite', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('created_at', models.DateTimeField(auto_now_add=True)), ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited_by', to='shop.product')), ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL))], options={'unique_together': {('user', 'product')}}),
    ]
