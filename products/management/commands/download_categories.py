import requests
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'
    def handle(self, *args, **options):
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
                categories = self.get_categories()
                return render(request, 'categories.html', {'categories': categories})

    print("Done")




