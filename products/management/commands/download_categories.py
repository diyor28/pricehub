import requests
from django.core.management.base import BaseCommand

from products.models import CategoriesModel


def category_box(categories):
    items = []
    for category in categories:
        if category["children"]:
            items += category_box(category["children"])
        else:
            items.append(category)
    return items


def get_categories():
    response = requests.get("https://api.umarket.uz/api/main/root-categories?eco=false",
                            headers={"Authorization": "Basic YjJjLWZyb250OmNsaWVudFNlY3JldA==",
                                     "Accept-Language": "ru-RU"})
    categories = response.json()["payload"]
    return category_box(categories[:100])


class Command(BaseCommand):
    help = 'Downloads categories from API'

    def handle(self, *args, **options):
        categories = get_categories()
        for category in categories:
            save_data = CategoriesModel(
                title=category["title"],
                remote_id=category["id"],
                source="uzum"
            )
            save_data.save()
        self.stdout.write(self.style.SUCCESS('Categories downloaded successfully.'))
