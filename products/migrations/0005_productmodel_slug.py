# Generated by Django 4.1.7 on 2023-04-03 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_delete_usermodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='productmodel',
            name='slug',
            field=models.SlugField(blank=True, null=True),
        ),
    ]
