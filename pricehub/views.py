from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View

from pricehub.forms import LoginForm
from products.management.commands.download_categories import get_categories
from products.models import ProductModel

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "authorization": "Basic YjJjLWZyb250OmNsaWVudFNlY3JldA=="
}


class HomePage(View):
    def get(self, request, *args, **kwargs):
        categories = [
            {"title": "Appliances"},
            {"title": "Auto Parts"},
            {"title": "Babies & Kids"},
            {"title": "Books & Magazines"},
            {"title": "Clothing"},
            {"title": "Computers"},
            {"title": "Digital Cameras"},
            {"title": "Books & Magazines"},
            {"title": "Clothing"},
            {"title": "Computers"},
            {"title": "Digital Cameras"},
            {"title": "Appliances"},
            {"title": "Auto Parts"},
            {"title": "Babies & Kids"},
            {"title": "Computers"},
            {"title": "Digital Cameras"},
            {"title": "Appliances"},
            {"title": "Auto Parts"},
            {"title": "Babies & Kids"}
        ]
        return render(request, 'index.html', context={"categories": categories})


class PriceComparator(View):
    template_name = "comparison.html"

    def get(self, request, p_id: int, p2_id: int, *args, **kwargs):
        productA = ProductModel.objects.get(id=p_id)
        productB = ProductModel.objects.get(id=p2_id)
        context = {'productA': productA, 'productB': productB}
        return render(request, "comparison.html", context)


class Login(View):
    def get(self, request, *args, **kwargs):
        return render(request, "login.html", context={})

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('/profile')

            # form is not valid or user is not authenticated
            messages.error(request, f'Invalid username or password')
        return redirect('/categories')


class CategoriesView(View):
    def get(self, request):
        categories = get_categories()
        return render(request, 'categories.html', {'categories': categories})


class ProfileView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/login')
        favorites = request.user.favorite_products.all()
        return render(request, 'profile.html', {"favorites": favorites})

class  ProductView(View):
    def get(self, request):
        return render(request, 'product.html')
