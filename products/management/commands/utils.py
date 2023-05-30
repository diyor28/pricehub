import asyncio
import random
import typing

GLOBAL_HEADERS = {
    "Accept-Language": "ru-RU",
    "Authorization": "Basic YjJjLWZyb250OmNsaWVudFNlY3JldA==",
    "x-content": "null",
    "apollographql-client-name": "web-customers",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "x-iid": "35224928-0d61-4330-9b34-6901e1cc5134"
}


def get_headers():
    h = GLOBAL_HEADERS.copy()
    h["x-iid"] = h["x-iid"].replace(str(random.randint(0, 9)), str(random.randint(0, 9)))
    return h


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


class AsyncPool:
    def __init__(self, workers: int):
        self.workers = workers
        self._executing: list[asyncio.Task] = []

    async def map(self, f: typing.Callable, iterable: typing.Iterable):
        for el in iterable:
            if len(self._executing) >= self.workers:
                _, pending = await asyncio.wait(self._executing, return_when=asyncio.FIRST_COMPLETED)
                self._executing = list(pending)
            self._executing.append(asyncio.create_task(f(el)))
        await asyncio.wait(self._executing, return_when=asyncio.ALL_COMPLETED)
