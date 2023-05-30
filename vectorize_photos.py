import os

import numpy as np
import tensorflow as tf
import tensorflow_hub as hub

from pricehub.products import timeit


def preprocess_image(image_path):
    image = tf.io.read_file(image_path)
    image = tf.image.decode_image(image, expand_animations=False, dtype=tf.float32)
    return tf.image.resize(image, [256, 256]) / 255


@timeit
def vectorize_photos(photo_folder_path, num_photos=10):
    vectorizer = tf.keras.Sequential([
        hub.KerasLayer("https://tfhub.dev/google/imagenet/inception_resnet_v2/feature_vector/5", trainable=False)
    ])
    vectorizer.build([None, 256, 256, 3])
    vectorizer.summary()

    image_files = os.listdir(photo_folder_path)[:num_photos]
    image_paths = [os.path.join(photo_folder_path, filename) for filename in image_files]
    ids = [int(os.path.splitext(filename)[0].replace("product_", "")) for filename in image_files]

    dataset = (
        tf.data.Dataset.from_tensor_slices(image_paths)
        .map(preprocess_image, num_parallel_calls=tf.data.AUTOTUNE)
        .batch(32)
        .prefetch(tf.data.AUTOTUNE)
    )

    vectors = vectorizer.predict(dataset)
    ids = np.array(ids, dtype=np.int32)
    return vectors, ids


def main():
    photo_folder_path = '../down_go/photos/'
    num_photos = 300_000

    vectors, ids = vectorize_photos(photo_folder_path, num_photos)
    np.savez('vectorized_features.npz', vectors=vectors, ids=ids)


if __name__ == '__main__':
    main()
