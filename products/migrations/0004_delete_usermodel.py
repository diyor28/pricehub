# Generated by Django 4.1.7 on 2023-04-03 10:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_usermodel'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserModel',
        ),
    ]
