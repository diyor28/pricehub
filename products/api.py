import random

from rest_framework import routers, serializers, viewsets

from products.models import ProductModel, CategoriesModel

random.seed(322)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriesModel
        fields = ['id', 'title', 'source']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = ProductModel
        fields = ('id', 'url', 'photo', 'price', 'title', 'category')


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
        price_gte = int(query_params.get("price_gte", "0"))
        price_lte = int(query_params.get("price_lte", "0"))
        source = query_params.get("source", "")

        if source:
            queryset = queryset.filter(category__source=source)

        queryset = queryset.order_by(sort)

        queryset = queryset.filter(price__gt=price_gt)
        if price_lt:
            queryset = queryset.filter(price__lt=price_lt)

        queryset = queryset.filter(price__gte=price_gte)
        if price_lte:
            queryset = queryset.filter(price__lte=price_lte)

        if q:
            queryset = queryset.filter(title__contains=q)

        queryset = queryset[offset:offset + limit]
        return queryset


router = routers.DefaultRouter()
router.register(r'products', ProductsViewSet, basename='products')
