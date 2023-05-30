from django.contrib.auth.models import User
from django.db import models


class AnchorCategoriesModel(models.Model):
    title = models.CharField(max_length=255)
    parent = models.ForeignKey("AnchorCategoriesModel", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = "anchor_categories"


class CategoriesModel(models.Model):
    title = models.CharField(max_length=255)
    remote_id = models.CharField(max_length=255)
    source = models.CharField(max_length=255, choices=(('uzum', 'uzum'),
                                                       ('zoodmall', 'zoodmall')))
    anchor = models.ForeignKey(AnchorCategoriesModel, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = "categories"


class ProductModel(models.Model):
    title = models.CharField(max_length=500)
    price = models.FloatField(db_index=True)
    photo = models.URLField(null=True, max_length=500)
    url = models.URLField(null=True)
    sku = models.CharField(max_length=255, null=True)
    anchor_category = models.ForeignKey(AnchorCategoriesModel, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(CategoriesModel, on_delete=models.SET_NULL, null=True)
    users = models.ManyToManyField(User, related_name='favorite_products')

    def __str__(self):
        return f"Product(title = {self.title}, photo={self.photo})"

    class Meta:
        db_table = "products"


class PriceHistory(models.Model):
    price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, related_name='prices')
