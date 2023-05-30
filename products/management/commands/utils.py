import random

import requests

GLOBAL_HEADERS = [
    {
        "Accept-Language": "ru-RU",
        "Authorization": "Basic YjJjLWZyb250OmNsaWVudFNlY3JldA==",
        "x-content": "null",
        "apollographql-client-name": "web-customers",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "x-iid": "787a2323-62b9-482f-a3b6-c364de775f7a"
    },
    {
        "Accept-Language": "ru-RU",
        "Authorization": "Basic YjJjLWZyb250OmNsaWVudFNlY3JldA==",
        "x-content": "null",
        "apollographql-client-name": "web-customers",
        "User-Agent": "*",
        "x-iid": "6cacf43c-9415-4170-bbde-97e352be8f44"
    },
    {
        "Accept-Language": "ru-RU",
        "Authorization": "Basic YjJjLWZyb250OmNsaWVudFNlY3JldA==",
        "x-content": "null",
        "apollographql-client-name": "web-customers",
        "User-Agent": "*",
        "x-iid": "8d6a1f0b-ab8d-4611-b29d-971b15d75795"
    },
    {
        "Accept-Language": "ru-RU",
        "Authorization": "Basic YjJjLWZyb250OmNsaWVudFNlY3JldA==",
        "x-content": "null",
        "apollographql-client-name": "web-customers",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "x-iid": "8098cb7e-9c45-4732-9252-1b63fcfbabfe"
    }
]


def get_headers():
    return random.choice(GLOBAL_HEADERS)

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


query = """
query getMakeSearch($queryInput: MakeSearchQueryInput!) {
  makeSearch(query: $queryInput) {
    items {
      catalogCard {
        minSellPrice
        productId
        title
        photos {
          link(trans: PRODUCT_540) {
            high
          }
        }
      }
    }
    total
  }
}
"""
