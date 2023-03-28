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

    class Meta:
        db_table = "categories"


class ProductModel(models.Model):
    title = models.CharField(max_length=255)
    price = models.FloatField()
    photo = models.URLField(null=True)
    url = models.URLField(null=True)
    anchor_category = models.ForeignKey(AnchorCategoriesModel, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(CategoriesModel, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Product(title={self.title})"

    class Meta:
        db_table = "products"
