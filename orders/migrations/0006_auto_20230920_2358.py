# Generated by Django 2.2.4 on 2023-09-20 23:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_auto_20230920_2006'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='dilivered',
            new_name='delivered',
        ),
    ]