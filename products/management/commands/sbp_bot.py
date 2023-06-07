import logging
from io import BytesIO
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from PIL import Image
from django.core.management.base import BaseCommand
from numba import njit, prange
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
from telegram.ext.filters import MessageFilter

from products.models import ProductModel

logger = logging.getLogger(__name__)


class PhotoFilter(MessageFilter):
    def filter(self, message):
        return bool(message.photo)


def preprocess_image(image):
    image = image.resize((256, 256))
    return np.array(image, dtype=np.float32)[np.newaxis] / 255


def load_features(file_path):
    data = np.load(file_path)
    vectors = data['vectors']
    product_ids = data['ids']
    return vectors, product_ids


@njit(parallel=True, fastmath=True)
def cosine_search(index, vector):
    v_norm = np.linalg.norm(vector)
    scores = np.zeros((index.shape[0],))
    for i in prange(index.shape[0]):
        scores[i] = np.dot(index[i], vector) / (np.linalg.norm(index[i]) * v_norm)
    return scores


class Command(BaseCommand):
    help = 'Starts the bot'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vectorizer = tf.keras.Sequential([
            hub.KerasLayer("https://tfhub.dev/google/imagenet/inception_resnet_v2/feature_vector/5", trainable=False)
        ])
        self.vectorizer.build([None, 256, 256, 3])
        data = np.load("vectorized_features.npz")
        self.vectors, self.product_ids = data["vectors"].astype(np.float32), data["ids"]

    def handle(self, *args, **options):
        token = '6001288764:AAHBfbPIcZUBWDNmFVDb9pBsn8moticRkrg'
        updater = Updater(token)
        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler("start", self.start_command))
        dispatcher.add_handler(MessageHandler(PhotoFilter(), self.image_received))

        updater.start_polling()
        updater.idle()

    @staticmethod
    def start_command(update: Update, context: CallbackContext):
        update.message.reply_text('Bot started. Send an image to find similar products.')

    def image_received(self, update: Update, context: CallbackContext):
        photo = update.message.photo[-1]
        image_file = context.bot.get_file(photo.file_id)
        image_data = image_file.download_as_bytearray()

        image = Image.open(BytesIO(image_data))
        vector = self.vectorizer.predict(preprocess_image(image), verbose=0)[0]
        scores = cosine_search(self.vectors, vector)

        n_closest = np.argsort(scores)[::-1][:5]
        closest_product_ids = self.product_ids[n_closest]

        products = ProductModel.objects.filter(id__in=closest_product_ids)

        for product in products:
            title = product.title
            price = product.price
            url = product.url
            photo_data = product.photo

            context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_data)

            response = f"{title}\n<b>{price}</b>\n{url}\n\n"
            update.message.reply_html(response)