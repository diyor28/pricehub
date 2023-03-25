from django.contrib import admin
from django.urls import path
from pricehub.views import HomePage, PriceComparator, Login, CategoriesView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomePage.as_view()),
    path('compare/', PriceComparator.as_view()),
    path('login/', Login.as_view()),
    path('categories/', CategoriesView.as_view(), name='categories'),
]
