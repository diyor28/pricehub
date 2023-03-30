from django.core.management.base import BaseCommand
from products.models import CategoriesModel, ProductModel
import requests


def variables(categoryId: int, offset: int, limit: int):
    return {
        "queryInput": {
            "categoryId": str(categoryId),
            "showAdultContent": "TRUE",
            "filters": [],
            "sort": "BY_ORDERS_NUMBER_DESC",
            "pagination": {
                "offset": offset,
                "limit": limit
            }
        }
    }


def _get_products(v):
    query = """
    query getMakeSearch($queryInput: MakeSearchQueryInput!) {
      makeSearch(query: $queryInput) {
        id
        queryId
        queryText
        items {
          catalogCard {
            __typename
            ...SkuGroupCardFragment
          }
          __typename
        }
        total
        mayHaveAdultContent
        __typename
      }
    }

    fragment SkuGroupCardFragment on SkuGroupCard {
      ...DefaultCardFragment
      __typename
    }

    fragment DefaultCardFragment on CatalogCard {
      feedbackQuantity
      id
      minFullPrice
      minSellPrice
      ordersQuantity
      productId
      rating
      title
      __typename
    }
    """
    response = requests.post("https://graphql.umarket.uz", json={
        "query": query,
        "variables": v,
    }, headers={
        "Accept-Language": "ru-RU",
        "User-Agent": "*",
        "x-iid": "627f65d5-f0e6-4e50-93b5-331a6d68b00c"
    })
    data = response.json()["data"]["makeSearch"]
    return data


def download_products(categoryId: int):
    products = []
    limit = 100
    for offset in range(0, 100_000, limit):
        data = _get_products(variables(categoryId, offset, limit))
        if not data["items"]:
            return
        products += data["items"]
        if data["total"] < offset + limit:
            break
    return products


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        # print(CategoriesModel.objects.filter(source='uzum'))
        uzum_categories = CategoriesModel.objects.filter(source='uzum')
        # download = download_products(products)
        for uzum_category in uzum_categories:
            products = download_products(int(uzum_category.remote_id))
            for data in products:
                saveData = ProductModel(title=data['catalogCard']['title'], price=data['catalogCard']['minSellPrice'], category_id=uzum_category.id,
                                        anchor_category_id=uzum_category.anchor_id)
                saveData.save()
