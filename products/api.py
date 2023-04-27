import random

from rest_framework import routers, serializers, viewsets

from products.models import ProductModel

random.seed(322)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModel
        fields = ['id', 'url', 'photo', 'price', 'title']


class ProductsViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = ProductModel.objects.all()
        query_params = self.request.query_params
        q = query_params.get('q', '')
        limit = int(query_params.get("limit", "100"))
        offset = int(query_params.get("offset", "0"))
        sort = query_params.get("sort", "id")
        price_gt = int(query_params.get("price_gt", "0"))
        price_lt = int(query_params.get("price_lt", "0"))

        queryset = queryset.order_by(sort)

        queryset = queryset.filter(price__gt=price_gt)
        if price_lt:
            queryset = queryset.filter(price__lt=price_lt)

        if q:
            queryset = queryset.filter(title__contains=q)

        queryset = queryset[offset:offset + limit]
        return queryset


router = routers.DefaultRouter()
router.register(r'products', ProductsViewSet, basename='products')
