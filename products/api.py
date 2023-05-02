import random
import time

from rest_framework import routers, serializers, viewsets
from rest_framework.response import Response

from products.models import ProductModel

random.seed(322)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModel
        fields = ['url', 'photo', 'price', 'title']


class ProductsViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = ProductModel.objects.all()
        q = self.request.query_params.get('q', '')
        if q:
            queryset = queryset.filter(title__contains='hello')
        return queryset


emojis = [
    '😀', '😃', '😄', '😁', '😆',
    '😅', '😂', '🤣', '🥲', '🥹',
    '😇', '🙂', '🙃', '😉', '😌',
    '😍', '🥰', '😘', '😗', '😙',
    '🥳', '😏', '😚', '😋', '😊',
    '😛', '😝', '😜', '🤪', '🤨',
    '🧐', '🤓', '😎', '🥸', '🤩',
    '😒', '😞', '😔', '😟', '😕',
    '🙁', '🫡', '🤔', '🫢', '😣',
    '😖', '😫', '😩', '🥺', '😢',
    '😭', '😮‍', '😤', '😠', '😡',
    '🤬', '🤯', '😳', '🥵', '🥶',
    '😱', '😨', '😰', '😥', '😓',
    '🫣', '🤗', '🤭', '🤫', '🤥'
]


class EmojisViewSet(viewsets.ViewSet):
    def list(self, request):
        time.sleep(1)
        return Response([random.choice(emojis)], status=200)


router = routers.DefaultRouter()
router.register(r'products', ProductsViewSet, basename='products')
router.register(r'emojis', EmojisViewSet, basename='emojis')
