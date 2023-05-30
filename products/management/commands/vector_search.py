import argparse

import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from django.core.management import BaseCommand
from numba import njit, prange

from products.models import ProductModel


@njit(parallel=True, fastmath=True)
def cosine_search(index, vector):
    v_norm = np.linalg.norm(vector)
    scores = np.zeros((index.shape[0],))
    for i in prange(index.shape[0]):
        scores[i] = np.dot(index[i], vector) / (np.linalg.norm(index[i]) * v_norm)
    return scores


class Command(BaseCommand):
    help = 'Vector search'

    @staticmethod
    def _build_model():
        model = tf.keras.Sequential([
            hub.KerasLayer("https://tfhub.dev/google/imagenet/inception_resnet_v2/feature_vector/5", trainable=False)
        ])
        model.build([None, 256, 256, 3])
        return model

    @staticmethod
    def _load_image(path: str):
        image = tf.io.read_file(path)
        image = tf.image.decode_image(image, expand_animations=False, channels=3, dtype=tf.float32)
        image = tf.image.resize(image, [256, 256]) / 255
        return tf.expand_dims(image, axis=0)

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument("--path", type=str)

    def handle(self, *args, path: str, **options):
        # preheat function
        cosine_search(np.random.random((32, 1536)).astype(np.float32), np.random.random((1536,)).astype(np.float32))

        data = np.load('vectorized_features.npz')
        index, product_ids = data['vectors'].astype(np.float32), data['ids']
        model = self._build_model()
        vector = model.predict(self._load_image(path), verbose=0)
        scores = cosine_search(index, vector[0])
        n_closest = np.argsort(scores)[::-1][:5]
        closest_product_ids = product_ids[n_closest]
        products = ProductModel.objects.filter(id__in=list(closest_product_ids))
        for p in products:
            print(p.pk, p.title, p.url)
