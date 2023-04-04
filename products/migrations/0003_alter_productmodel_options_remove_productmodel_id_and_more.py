# Generated by Django 4.1.7 on 2023-04-03 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_alter_anchorcategoriesmodel_parent'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productmodel',
            options={'ordering': ['product_id']},
        ),
        migrations.RemoveField(
            model_name='productmodel',
            name='id',
        ),
        migrations.AddField(
            model_name='productmodel',
            name='product_id',
            field=models.AutoField(default=None, primary_key=True, serialize=False),
        ),
    ]
