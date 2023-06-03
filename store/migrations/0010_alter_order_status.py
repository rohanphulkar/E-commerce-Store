# Generated by Django 4.2.1 on 2023-06-03 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending', 'pending'), ('failed', 'failed'), ('success', 'success')], default='pending', max_length=50),
        ),
    ]