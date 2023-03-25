from django.db import models


class ProductModel(models.Model):
    title = models.CharField(max_length=255)
    price = models.FloatField()
    photo = models.URLField(null=True)
    url = models.URLField(null=True)

class Categories(models.Model):
    title = models.CharField(max_length=255)
