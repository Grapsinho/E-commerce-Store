# Generated by Django 5.0.2 on 2024-04-02 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0016_remove_cart_added_at_remove_cart_product_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shippingaddress',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='shippingaddress',
            name='name',
        ),
        migrations.AddField(
            model_name='shippingaddress',
            name='full_name',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
