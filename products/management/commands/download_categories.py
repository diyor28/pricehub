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
    return category_box(categories)


class Command(BaseCommand):
    help = 'Downloads categories from API'

    def handle(self, *args, **options):
        categories = get_categories()
        to_be_saved = [CategoriesModel(title=cat["title"], remote_id=cat["id"], source="uzum") for cat in categories]
        CategoriesModel.objects.bulk_create(to_be_saved)
        self.stdout.write(self.style.SUCCESS('Categories downloaded successfully.'))
