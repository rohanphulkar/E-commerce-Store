# Generated by Django 4.2.1 on 2023-05-24 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_remove_cartitem_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='subtotal',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
    ]
