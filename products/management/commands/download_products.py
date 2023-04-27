from concurrent.futures import ThreadPoolExecutor

import requests
from django.core.management.base import BaseCommand

from pricehub.products import timeit
from products.models import CategoriesModel, ProductModel

session = requests.Session()


def translit(text):
    map = {
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "g",
        "д": "d",
        "е": "ye",
        "ё": "yo",
        "ж": "j",
        "з": "z",
        "и": "i",
        "й": "y",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "x",
        "ц": "ts",
        "ч": "ch",
        "щ": "sh",
        "ъ": "",
        "ы": "i",
        "ь": "",
        "э": "e",
        "ю": "yu",
        "я": "ya",
    }
    result = ""
    for i, l in enumerate(text.lower()):
        t = map.get(l, l)
        result += t.upper() if text[i].isupper() else t
    return result


def title_to_link(title: str):
    parts = title.split(" ")
    if len(parts) > 5:
        parts = parts[:3]
    title = "-".join(parts)
    result = "".join(l for l in title if l.isalpha() or l == "-")
    return "https://uzum.uz/ru/product/" + translit(result)


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
      photos {
        key
        link(trans: PRODUCT_540) {
          high
          low
          __typename
        }
        previewLink: link(trans: PRODUCT_240) {
          high
          low
          __typename
        }
        __typename
      }
    }
    """
    response = session.post("https://graphql.umarket.uz", json={
        "query": query,
        "variables": v,
    }, headers={
        "Accept-Language": "ru-RU",
        "Authorization": "Basic YjJjLWZyb250OmNsaWVudFNlY3JldA==",
        "x-content": "null",
        "apollographql-client-name": "web-customers",
        "User-Agent": "*",
        "x-iid": "787a2323-62b9-482f-a3b6-c364de775f7a"
    })
    resp = response.json()
    if resp.get("errors"):
        raise ValueError(resp.get("errors"))
    data = resp["data"]["makeSearch"]
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
    return [p["catalogCard"] for p in products]


def download_for_category(category):
    products = download_products(int(category.remote_id))
    to_be_saved = []
    for p in products:
        product = ProductModel(
            title=p['title'],
            price=p['minSellPrice'],
            category_id=category.id,
            anchor_category_id=category.anchor_id,
            photo=p['photos'][0]['link']['high'],
            url=title_to_link(p['title']) + f"-{p['id']}"
        )
        to_be_saved.append(product)
    ProductModel.objects.bulk_create(to_be_saved)


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    @timeit
    def handle(self, *args, **options):
        ids = [1251, 1252, 1253, 1254, 1255, 1256,
               1257, 1258, 1259, 1260, 1267,
               1268, 1269, 1270, 1271, 1272, 1273,
               1274, 1275, 1276, 1277, 1278, 1279]
        uzum_categories = CategoriesModel.objects.filter(id__in=ids)
        futures = []
        with ThreadPoolExecutor(10) as executor:
            for uzum_category in uzum_categories:
                rs = executor.submit(download_for_category, uzum_category)
                futures.append(rs)

        for ft in futures:
            ft.result()
