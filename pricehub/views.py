import requests
from django.shortcuts import render, redirect
from django.views.generic import View
from pricehub.forms import LoginForm
from products.models import ProductModel, CategoriesModel
from products.management.commands.download_categories import get_categories
from products.models import ProductModel


headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36", "authorization": "Basic YjJjLWZyb250OmNsaWVudFNlY3JldA=="
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

    def get(self, request, p_id: int, *args, **kwargs):
        # print(p_id)
        productA = ProductModel.objects.get(category_id=p_id )
        # productB = ProductModel.objects.get(category_id=p_id)
        context = {'productA': productA}
        # print(p_id)
        # products = []
        # phoneA = {}
        # phoneB = {}
        # context = {'products': products, 'phoneA': phoneA, 'phoneB': phoneB}
        return render(request, "comparison.html", context)


class Login(View):
    def get(self, request, *args, **kwargs):
        return render(request, "login.html", context={})

    def post(self, request, *args, **kwargs):
        pass

class CategoriesView(View):
    def category_box(self, categories):
        items = []
        for category in categories:
            if category["children"]:
                items += self.category_box(category["children"])
            else:
                items.append(category)
        return items

    def get_categories(self):
        response = requests.get("https://api.umarket.uz/api/main/root-categories?eco=false",
                                headers={"Authorization": "Basic YjJjLWZyb250OmNsaWVudFNlY3JldA==",
                                         "Accept-Language": "ru-RU"})
        categories = response.json()["payload"]
        return self.category_box(categories[:100])

    def get(self, request):
        categories = get_categories()
        return render(request, 'categories.html', {'categories': categories})


