from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from rest_framework.filters import SearchFilter
from products.models import ProductModel, UserModel


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModel
        fields = ['url', 'photo', 'price', 'title']


class ProductsViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = ProductModel.objects.filter(title__contains=self.request.query_params['q'])
        return queryset


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['email', 'password']


class UsersViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = UserModel.objects.all()
        return queryset


router = routers.DefaultRouter()
router.register(r'products', ProductsViewSet, basename='products')

router_user = routers.DefaultRouter()
router_user.register(r'users', UsersViewSet, basename='users')