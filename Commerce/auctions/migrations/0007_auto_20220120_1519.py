# Generated by Django 2.2.12 on 2022-01-20 15:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_bid_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bid',
            old_name='status',
            new_name='active',
        ),
    ]
