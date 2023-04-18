from threading import Thread

import requests
from django.core.management.base import BaseCommand

from pricehub.products import timeit
from products.models import CategoriesModel, ProductModel


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


@timeit
def download_for_category(category):
    products = download_products(int(category.remote_id))
    to_be_saved = []
    for p in products:
        product = ProductModel(title=p['catalogCard']['title'],
                               price=p['catalogCard']['minSellPrice'],
                               category_id=category.id,
                               anchor_category_id=category.anchor_id,
#                               photo=photo url for this product
#                               url=https://uzum.uz/ru/product/ + translit() + '-' + id
                               )
        to_be_saved.append(product)
    ProductModel.objects.bulk_create(to_be_saved)


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    @timeit
    def handle(self, *args, **options):
        ids = [1251, 1252, 1253, 1254, 1255, 1256, 1257, 1258, 1259, 1260]
        uzum_categories = CategoriesModel.objects.filter(id__in=ids)
        threads = []
        for uzum_category in uzum_categories:
            p = Thread(target=download_for_category, args=[uzum_category])
            threads.append(p)

        for th in threads:
            th.start()

        for th in threads:
            th.join()
