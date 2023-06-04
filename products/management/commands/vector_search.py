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
    def _build_model():
        model = tf.keras.applications.ResNet50V2(pooling='avg', include_top=False, input_shape=(224, 224, 3))
        model.load_weights(os.path.join(settings.BASE_DIR, 'encoder.h5'))
        model.compile(jit_compile=True)
        model.summary()
        return model

    @staticmethod
    def _load_image(path: str):
        image = tf.io.read_file(path)
        image = tf.image.decode_image(image, expand_animations=False, channels=3, dtype=tf.float32)
        image = tf.image.resize(image, [224, 224])
        return tf.expand_dims(tf.keras.applications.resnet_v2.preprocess_input(image), axis=0)

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument("--path", type=str)

    def handle(self, *args, path: str, **options):
        # preheat function
        l2_distance(np.random.random((32, 1280)).astype(np.float32), np.random.random((1280,)).astype(np.float32))
        data = np.load(os.path.join(settings.BASE_DIR, 'index.npz'))
        index, product_ids = data['vectors'].astype(np.float32), data['ids']
        model = self._build_model()
        image = self._load_image(path)
        vector = model.predict(image, verbose=0)
        scores = l2_distance(index, vector[0])
        n_closest = np.argsort(scores)[:5]
        closest_product_ids = product_ids[n_closest]
        print(np.min(scores), np.max(scores))
        products = ProductModel.objects.filter(id__in=list(closest_product_ids))
        for p in products:
            print(p.pk, p.title, p.url)
