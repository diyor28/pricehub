import requests
from django.shortcuts import render, redirect
from django.views.generic import View

from pricehub.forms import LoginForm
from products.models import ProductModel

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}
users = {
    "ozod@gmail.com": {
        "firstName": "Ozod",
        "lastName": "Shukurov",
        "password": "1234"
    },
    "amir@gmail.com": {
        "firstName": "Amir",
        "lastName": "Akhtamov",
        "password": "qwerty123"
    },
    "ibrogim@gmail.com": {
        "firstName": "Ibrogim",
        "lastName": "Miraliev",
        "password": "pass123"
    }
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
        products = ProductModel.objects.all()
        return render(request, 'index.html', context={"categories": categories, "products": products})


class PriceComparator(View):
    template_name = "comparison.html"

    def get(self, request, *args, **kwargs):
        phone_a = "https://api.umarket.uz/api/v2/product/231855"
        phone_b = "https://api.umarket.uz/api/v2/product/287201"
        response_a = requests.get(phone_a, headers=headers).json()
        response_b = requests.get(phone_b, headers=headers).json()
        product_a = response_a["payload"]["data"]
        product_b = response_b["payload"]["data"]
        context = {
            "phoneA": {
                "title": product_a["title"],
                "url": product_a["photos"][0]["photo"]["800"]["high"],
                "CPU": product_a["attributes"][0],
                "mainCam": product_a["attributes"][8]
            },
            "phoneB": {
                "title": product_b["title"],
                "url": product_b["photos"][0]["photo"]["800"]["high"],
                "CPU": product_b["attributes"][1],
                "mainCam": product_b["attributes"][3]
            }
        }
        return render(request, "comparison.html", context=context)


class Login(View):
    def get(self, request, *args, **kwargs):
        return render(request, "login.html", context={})

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if not form.is_valid():
            return render(request, "login.html", context={"error": "The form has been filled out incorrectly check email and password"})

        user = users.get(form.cleaned_data['email'], None)
        if user is None:
            return render(request, "login.html", context={"error": "login is incorrect"})

        saved_password = user["password"]
        if form.cleaned_data['password'] != saved_password:
            return render(request, "login.html", context={"error": "password is incorrect"})

        return redirect('/')


from django.views import View
from django.shortcuts import render
import requests

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
        response = requests.get("https://api.umarket.uz/api/main/root-categories?eco=false", headers={"Authorization": "Basic YjJjLWZyb250OmNsaWVudFNlY3JldA==", "Accept-Language": "ru-RU"})
        categories = response.json()["payload"]
        return self.category_box(categories[:100])

    def get(self, request):
        categories = self.get_categories()
        return render(request, 'categories.html', {'categories': categories})