from concurrent.futures import ThreadPoolExecutor

import tqdm
from django.core.management.base import BaseCommand

from pricehub.products import timeit
from products.management.commands.utils import download_products, get_sku_list, title_to_link
from products.models import CategoriesModel, ProductModel, PriceHistory


def download_for_category(category):
    products = download_products(int(category.remote_id))
    skus = get_sku_list([p["id"] for p in products])
    new_products = []
    new_skus = []
    for prod, sku in zip(products, skus):
        if sku is not None:
            new_products.append(prod)
            new_skus.append(sku)
    products = new_products
    skus = new_skus

    to_be_saved = []

    for p, sku in zip(products, skus):
        price = p["minSellPrice"]
        title = p["title"]
        photo = p["photos"][0]["link"]["high"]
        url = title_to_link(p["title"]) + f"-{p['id']}"
        try:
            existing_product = ProductModel.objects.get(sku=sku)
            existing_product.title = title
            existing_product.price = price
            existing_product.photo = photo
            existing_product.url = url
            ph = PriceHistory(price=price)
            ph.save()
            existing_product.prices.add(ph)
            existing_product.save()
            continue
        except ProductModel.DoesNotExist:
            product = ProductModel(
                title=title,
                sku=sku,
                price=price,
                category_id=category.id,
                anchor_category_id=category.anchor_id,
                photo=photo,
                url=url
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
        with ThreadPoolExecutor(10) as executor:
            list(tqdm.tqdm(executor.map(download_for_category, uzum_categories), total=len(uzum_categories)))