# Generated by Django 4.1.7 on 2023-04-27 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_alter_anchorcategoriesmodel_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productmodel',
            name='price',
            field=models.FloatField(db_index=True),
        ),
    ]
