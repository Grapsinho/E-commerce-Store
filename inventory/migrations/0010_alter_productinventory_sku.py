# Generated by Django 5.0.2 on 2024-03-20 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0009_product_unique_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productinventory',
            name='sku',
            field=models.CharField(max_length=120),
        ),
    ]