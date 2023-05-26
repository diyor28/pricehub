from django.core.management.base import BaseCommand
import os
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import time


def preprocess_image(image_path):
    image = tf.io.read_file(image_path)
    image = tf.image.decode_jpeg(image, channels=3)
    image = tf.image.resize(image, [256, 256])
    image = tf.cast(image, tf.float32) / 255.0
    return image


class Command(BaseCommand):
    help = 'Vectorize photos using TensorFlow'

    def add_arguments(self, parser):
        parser.add_argument('photo_folder_path', type=str, help='Path to the folder containing the photos')
        parser.add_argument('num_photos', type=int, default=10, nargs='?', help='Number of photos to vectorize')

    def handle(self, *args, **options):
        photo_folder_path = options['photo_folder_path']
        num_photos = options['num_photos']

        start_time = time.time()

        vectors, ids = self.vectorize_photos(photo_folder_path, num_photos)
        self.stdout.write(self.style.SUCCESS(f'Features shape: {vectors.shape}'))

        ids = ids.astype(np.int32)
        vectors = vectors.astype(np.float32)

        end_time = time.time()
        execution_time = end_time - start_time
        self.stdout.write(self.style.SUCCESS(f'Execution time: {execution_time:.2f} seconds'))

        output_file = 'vectorized_features.npz'
        self.save_features(vectors, ids, output_file)
        self.stdout.write(self.style.SUCCESS(f'Vectorized features saved to: {output_file}'))

    def vectorize_photos(self, photo_folder_path, num_photos=10):
        vectorizer = tf.keras.Sequential([
            hub.KerasLayer("https://tfhub.dev/google/imagenet/inception_resnet_v2/feature_vector/5", trainable=False)
        ])
        vectorizer.build([None, 256, 256, 3])

        image_files = os.listdir(photo_folder_path)[:num_photos]
        image_paths = [os.path.join(photo_folder_path, filename) for filename in image_files]
        ids = [os.path.splitext(filename)[0].replace("product_", "") for filename in image_files]

        dataset = tf.data.Dataset.from_tensor_slices(image_paths)

        dataset = dataset.map(preprocess_image, num_parallel_calls=tf.data.AUTOTUNE)
        dataset = dataset.batch(16)

        # Vectorize images
        vectors = []
        for batch in dataset:
            batch_vectors = vectorizer.predict(batch)
            vectors.extend(batch_vectors)

        vectors = np.array(vectors)
        ids = np.array(ids)
        return vectors, ids

    def save_features(self, vectors, ids, output_file):
        np.savez(output_file, vectors=vectors, ids=ids)


if __name__ == '__main__':
    command = Command()
    command.execute()
