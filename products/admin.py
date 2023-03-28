from django.contrib import admin

from .models import ProductModel, CategoriesModel, AnchorCategoriesModel


@admin.register(AnchorCategoriesModel)
class AnchorCategoriesAdmin(admin.ModelAdmin):
    pass

@admin.register(CategoriesModel)
class CategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(ProductModel)
class ProductAdmin(admin.ModelAdmin):
    pass
# Register your models here.
