import argparse
import logging
import os

import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from django.core.management.base import BaseCommand
from numba import njit, prange
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from products.models import ProductModel

os.environ['CUDA_VISIBLE_DEVICES'] = "-1"


@njit(parallel=True, fastmath=True)
def l2_distance(index, vector):
    scores = np.zeros((index.shape[0],))
    for i in prange(index.shape[0]):
        scores[i] = np.linalg.norm(index[i] - vector)
    return scores


class Command(BaseCommand):
    help = 'Starts the Product Search Bot'

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument('--token', type=str, help='Telegram Bot token',
                            default="6001288764:AAHBfbPIcZUBWDNmFVDb9pBsn8moticRkrg")
        parser.add_argument('--index', type=str, help='Path to the index directory', default="data")

    def handle(self, *args, **options):
        token = options['token']
        index_dir = options['index']

        bot_handler = BotHandler(token, index_dir)
        bot_handler.start()


class BotHandler:
    def __init__(self, token, index_dir):
        self.token = token
        self.index_dir = index_dir
        self.model = None
        self.index = None
        self.product_ids = None

    def start(self):
        self._load_model()
        self._load_index()
        self._create_bot()

    def _load_model(self):
        self.model = self._build_model()

    def _load_index(self):
        data = np.load(os.path.join(self.index_dir, 'index.npz'))
        self.index = data['vectors'].astype(np.float32)
        self.product_ids = data['ids']

    @staticmethod
    def _build_model():
        m = tf.keras.Sequential([
            hub.KerasLayer("https://tfhub.dev/tensorflow/efficientnet/lite0/feature-vector/2", trainable=False)
        ])
        m.build((None, 224, 224, 3))
        return m

    @staticmethod
    def _load_image(path):
        image = tf.io.read_file(path)
        image = tf.image.decode_image(image, expand_animations=False, channels=3)
        image = tf.image.resize(image, (224, 224)) / 255
        return tf.expand_dims(image, axis=0)

    def _process_image(self, image):
        vector = self.model.predict(image, verbose=0)
        scores = l2_distance(self.index, vector[0])
        n_closest = np.argsort(scores)[:3]
        closest_product_ids = self.product_ids[n_closest.tolist()]
        return ProductModel.objects.filter(id__in=closest_product_ids)

    def _create_bot(self):
        updater = Updater(self.token, use_context=True)
        dispatcher = updater.dispatcher

        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

        start_handler = CommandHandler('start', self._start)
        photo_handler = MessageHandler(Filters.photo, self._handle_photo)

        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(photo_handler)

        updater.start_polling()

    def _start(self, update: Update, context: CallbackContext):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Welcome to the Product Search Bot!')

    def _handle_photo(self, update: Update, context: CallbackContext):
        file_id = update.message.photo[-1].file_id
        file = context.bot.get_file(file_id)
        file_path = file.file_path
        image_path = os.path.join('data', os.path.basename(file_path))
        file.download(image_path)
        products = self._process_image(self._load_image(image_path))

        for product in products:
            title = product.title
            price = product.price
            url = product.url
            photo_data = product.photo

            context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_data)

            response = f"{title}\n<b>{price}</b>\n{url}\n\n"
            update.message.reply_html(response)
