# Generated by Django 5.0.2 on 2024-03-28 09:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0013_alter_wishlist_products_alter_wishlistitem_product'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_prod', to='inventory.productinventory')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cart_owner', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
