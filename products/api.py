from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phone
        fields = ['url', 'photo', 'price', 'title']
