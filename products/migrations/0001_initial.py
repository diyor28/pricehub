# Generated by Django 4.1.7 on 2023-03-25 15:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AnchorCategoriesModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='products.anchorcategoriesmodel')),
            ],
            options={
                'db_table': 'anchor_categories',
            },
        ),
        migrations.CreateModel(
            name='CategoriesModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('remote_id', models.CharField(max_length=255)),
                ('source', models.CharField(choices=[('uzum', 'uzum'), ('zoodmall', 'zoodmall')], max_length=255)),
                ('anchor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.anchorcategoriesmodel')),
            ],
            options={
                'db_table': 'categories',
            },
        ),
        migrations.CreateModel(
            name='ProductModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('price', models.FloatField()),
                ('photo', models.URLField(null=True)),
                ('url', models.URLField(null=True)),
                ('anchor_category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.anchorcategoriesmodel')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.categoriesmodel')),
            ],
            options={
                'db_table': 'products',
            },
        ),
    ]
