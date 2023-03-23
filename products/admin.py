from django.contrib import admin
from .models import ProductModel
@admin.register(ProductModel)
class ProductAdmin(admin.ModelAdmin):
    pass
# Register your models here.
