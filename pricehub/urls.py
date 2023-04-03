from django.contrib import admin
from django.urls import path, include
from pricehub.views import HomePage, PriceComparator, Login, CategoriesView
from products.api import router

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomePage.as_view()),
    path('compare/<int:p_id>/', PriceComparator.as_view()),
    path('login/',Login.as_view()),
    path('api/', include(router.urls)),
    path('categories/', CategoriesView.as_view(), name='categories'),
]
