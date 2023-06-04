import glob
import os

import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from django.core.management import BaseCommand

from pricehub import settings
from pricehub.products import timeit

# tf.keras.mixed_precision.set_global_policy("mixed_float16")

gpus = tf.config.list_physical_devices('GPU')
for device in gpus:
    print("Setting memory growth on:", device.name)
    tf.config.experimental.set_memory_growth(device, True)


def preprocess_image(image_path):
    image = tf.io.read_file(image_path)
    image = tf.image.decode_image(image, expand_animations=False, channels=3, dtype=tf.float32)
    return tf.image.resize(image, [224, 224]) / 255


@timeit
def vectorize_photos(photo_folder_path, num_photos=10):
    vectorizer = tf.keras.Sequential([
        hub.KerasLayer("https://tfhub.dev/tensorflow/efficientnet/lite0/feature-vector/2", trainable=False)
    ])
    vectorizer.build((None, 224, 224, 3))
    vectorizer.summary()

    image_files = glob.glob(photo_folder_path + '\\*\\*')[:num_photos]
    ids = [int(filename.split("\\")[-1].split("_")[1]) for filename in image_files]

    dataset = (
        tf.data.Dataset.from_tensor_slices(image_files)
        .map(preprocess_image, num_parallel_calls=tf.data.AUTOTUNE)
        .batch(256)
        .prefetch(tf.data.AUTOTUNE)
    )

    vectors = vectorizer.predict(dataset)
    ids = np.array(ids, dtype=np.int32)
    return vectors.astype(np.float16), ids


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        photo_folder_path = os.path.join(settings.BASE_DIR.parent, 'photos')
        num_photos = 200_000

        vectors, ids = vectorize_photos(photo_folder_path, num_photos)
        np.savez(os.path.join(settings.BASE_DIR, 'index2.npz'), vectors=vectors, ids=ids)
