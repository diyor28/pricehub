from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from rest_framework.filters import SearchFilter
from products.models import ProductModel


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModel
        fields = ['url', 'photo', 'price', 'title']


class ProductsViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = ProductModel.objects.filter(title__contains=self.request.query_params['q'])
        return queryset


router = routers.DefaultRouter()
router.register(r'products', ProductsViewSet, basename='products')
