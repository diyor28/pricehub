import asyncio

import httpx
import requests

GLOBAL_HEADERS = {
    "Accept-Language": "ru-RU",
    "Authorization": "Basic YjJjLWZyb250OmNsaWVudFNlY3JldA==",
    "x-content": "null",
    "apollographql-client-name": "web-customers",
    "User-Agent": "*",
    "x-iid": "787a2323-62b9-482f-a3b6-c364de775f7a"
}

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


async def _get_products(client: httpx.AsyncClient, v):
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
    response = await client.post("https://graphql.umarket.uz", json={
        "query": query,
        "variables": v,
    }, headers=GLOBAL_HEADERS)
    resp = response.json()
    if resp.get("errors"):
        raise ValueError(resp.get("errors"))
    data = resp["data"]["makeSearch"]
    return data


async def download_products(categoryId: int):
    products = []
    limit = 100
    limits = httpx.Limits(max_keepalive_connections=10, max_connections=50)
    async with httpx.AsyncClient(http2=True, limits=limits, timeout=20) as client:
        for offset in range(0, 100_000, limit):
            data = await _get_products(client, variables(categoryId, offset, limit))
            if not data["items"]:
                return
            products += [p["catalogCard"] for p in data["items"]]
            if data["total"] < offset + limit:
                break
        skus = await asyncio.gather(*[get_sku(client, p["id"]) for p in products])
        for p, sku in zip(products, skus):
            p["sku"] = sku
    return products


async def get_sku(client: httpx.AsyncClient, product_id: str):
    url = f"https://api.uzum.uz/api/v2/product/{product_id}"
    resp = await client.get(url, headers=GLOBAL_HEADERS)
    data = resp.json()
    if resp.status_code not in [200, 201] or not data["payload"]:
        return None
    if not data["payload"]["data"]["skuList"]:
        return None
    return data["payload"]["data"]["skuList"][0]["id"]
