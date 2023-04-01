from django.core.management.base import BaseCommand
from products.models import CategoriesModel
import requests


class CategoriesView:
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
        print(response.json()["payload"])
        return self.category_box(categories[:100])


class Command(BaseCommand):
    help = 'Downloads categories from API'

    def handle(self, *args, **options):
        categories_view = CategoriesView()
        categories = categories_view.get_categories()
        for category in categories:
            save_data = CategoriesModel()
            save_data.save()
        self.stdout.write(self.style.SUCCESS('Categories downloaded successfully.'))
