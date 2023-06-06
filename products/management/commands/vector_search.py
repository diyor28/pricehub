import argparse
import os

from pricehub import settings
from pricehub.products import timeit

os.environ['CUDA_VISIBLE_DEVICES'] = "-1"
import numpy as np
import tensorflow as tf
from django.core.management import BaseCommand
from numba import njit, prange

from products.models import ProductModel
import tensorflow_hub as hub


@njit(parallel=True, fastmath=True)
def cosine_search(index, vector):
    v_norm = np.linalg.norm(vector)
    scores = np.zeros((index.shape[0],))
    for i in prange(index.shape[0]):
        scores[i] = np.dot(index[i], vector) / (np.linalg.norm(index[i]) * v_norm)
    return scores


@timeit
@njit(parallel=True, fastmath=True)
def l2_distance(index, vector):
    scores = np.zeros((index.shape[0],))
    for i in prange(index.shape[0]):
        scores[i] = np.linalg.norm(index[i] - vector)
    return scores


class Command(BaseCommand):
    help = 'Vector search'

    @staticmethod
    def _build_custom_model():
        mnet = tf.keras.applications.MobileNetV3Large(input_shape=(224, 224, 3))
        logits = tf.keras.layers.Conv2D(1137, kernel_size=1, padding="same", name="Logits")(mnet.layers[-4].output)
        flat = tf.keras.layers.Flatten(name="flatten")(logits)
        m = tf.keras.Model(inputs=mnet.inputs, outputs=[flat])
        m.compile()
        return m

    @staticmethod
    def _build_model():
        m = tf.keras.Sequential([
            hub.KerasLayer("https://tfhub.dev/tensorflow/efficientnet/lite0/feature-vector/2", trainable=False)
        ])
        m.build((224, 224, 3))
        return m

    @staticmethod
    def _load_image(path: str):
        image = tf.io.read_file(path)
        image = tf.image.decode_image(image, expand_animations=False, channels=3)
        image = tf.image.resize(image, (224, 224))
        return tf.expand_dims(image, axis=0)

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument("--path", type=str)

    def handle(self, *args, path: str, **options):
        # preheat function
        l2_distance(np.random.random((32, 2048)).astype(np.float32), np.random.random((2048,)).astype(np.float32))
        data = np.load(os.path.join(settings.BASE_DIR, 'data/index.npz'))
        index, product_ids = data['vectors'].astype(np.float32), data['ids']
        model = self._build_model()
        vector = model.predict(self._load_image(path), verbose=0)
        scores = l2_distance(index, vector[0])
        n_closest = np.argsort(scores)[:5]
        closest_product_ids = product_ids[n_closest]
        products = ProductModel.objects.filter(id__in=list(closest_product_ids))
        for p in products:
            print(p.pk, p.title, p.url)
