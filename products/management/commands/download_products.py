import asyncio
from concurrent.futures import ThreadPoolExecutor

import tqdm
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand

from pricehub.products import timeit
from products.management.commands.utils import download_products, title_to_link
from products.models import CategoriesModel, ProductModel, PriceHistory


async def download_for_category(category: CategoriesModel):
    products = await download_products(int(category.remote_id))

    to_be_created = []
    to_be_updated = []
    to_be_created_ph = []

    for p in products:
        price = p["minSellPrice"]
        title = p["title"]
        photo = p["photos"][0]["link"]["high"]
        sku = p["sku"]
        url = title_to_link(p["title"]) + f"-{p['id']}"
        try:
            if not sku:
                raise ProductModel.DoesNotExist("Bullshit")
            existing_product = await sync_to_async(ProductModel.objects.get)(sku=sku)
            existing_product.title = title
            existing_product.price = price
            existing_product.photo = photo
            existing_product.url = url
            to_be_created_ph.append(PriceHistory(price=price, product_id=existing_product.pk))
            to_be_updated.append(existing_product)
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
            to_be_created.append(product)

    await asyncio.gather(
        sync_to_async(PriceHistory.objects.bulk_create)(to_be_created_ph),
        sync_to_async(ProductModel.objects.bulk_create)(to_be_created),
        sync_to_async(ProductModel.objects.bulk_update)(to_be_updated, fields=['title', 'price', 'photo', 'url'])
    )


async def download_multiple_categories(categories):
    await asyncio.gather(*[download_for_category(cat) for cat in categories])


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    @timeit
    def handle(self, *args, **options):
        uzum_categories = list(CategoriesModel.objects.all()[:100])
        for i in tqdm.tqdm(range(0, len(uzum_categories), 5)):
            asyncio.run(download_multiple_categories(uzum_categories[i:i + 5]))
