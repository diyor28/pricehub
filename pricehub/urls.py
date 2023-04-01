from django.contrib import admin
from django.urls import path, include
from pricehub.views import HomePage, PriceComparator, Login, CategoriesView
from products.api import router, router_user

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomePage.as_view()),
    path('compare/', PriceComparator.as_view()),
    path('login/',Login.as_view()),
    path('api/', include(router.urls)),
    path('api/auth/', include(router_user.urls)),
    path('categories/', CategoriesView.as_view(), name='categories'),
]
