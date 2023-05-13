import random

from rest_framework import routers, serializers, viewsets
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import ProductModel

random.seed(322)

from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


class AddToFavoritesApi(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, SessionAuthentication)

    def post(self, request):
        product_id = request.POST.get('product_id')
        if not product_id:
            raise ParseError(detail='field product_id is required')
        product = ProductModel.objects.get(pk=product_id)
        product.users.add(request.user.id)
        return Response({"ok": True})


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
        return queryset


router = routers.DefaultRouter()
router.register(r'products', ProductsViewSet, basename='products')
