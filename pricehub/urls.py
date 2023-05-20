from django.contrib import admin
from django.urls import path, include

from pricehub.views import HomePage, PriceComparator, Login, CategoriesView, ProfileView, ProductView
from products.api import router, AddToFavoritesApi

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomePage.as_view()),
    path('compare/<int:p_id>/<int:p2_id>/', PriceComparator.as_view()),
    path('login/', Login.as_view()),
    path('api/', include(router.urls)),
    path('api/like/', AddToFavoritesApi.as_view()),
    path('categories/', CategoriesView.as_view(), name='categories'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('product/', ProductView.as_view()),
]
