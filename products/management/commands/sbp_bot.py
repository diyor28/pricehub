# SBP BOT CODE
from django.core.management.base import BaseCommand
from PIL import Image
from io import BytesIO
import logging
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from telegram import Update, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
from telegram.ext.filters import MessageFilter

logger = logging.getLogger(__name__)

vectorizer = None
vectors = None
product_ids = None

class PhotoFilter(MessageFilter):
    def filter(self, message):
        return bool(message.photo)

def preprocess_image(image):
    image = image.resize((256, 256))
    image = np.array(image)
    image = tf.cast(image, tf.float32) / 255.0
    return image


def load_features(file_path):
    data = np.load(file_path)
    vectors = data['vectors']
    product_ids = data['ids']
    return vectors, product_ids


def cosine_search(vectorizer, index, vector):
    v_norm = np.linalg.norm(vector)
    vector = tf.expand_dims(vector, axis=0)
    vector = vectorizer.predict(vector)[0]
    scores = np.dot(index, vector) / (np.linalg.norm(index, axis=1) * v_norm)
    return scores


class Command(BaseCommand):
    help = 'Starts the bot'

    def handle(self, *args, **options):
        global vectorizer, vectors, product_ids

        token = '6001288764:AAHBfbPIcZUBWDNmFVDb9pBsn8moticRkrg'
        file_path = 'vectorized_features.npz'

        vectorizer = tf.keras.Sequential([
            hub.KerasLayer("https://tfhub.dev/google/imagenet/inception_resnet_v2/feature_vector/5", trainable=False)
        ])
        vectorizer.build([None, 256, 256, 3])

        vectors, product_ids = load_features(file_path)

        updater = Updater(token)
        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler("start", self.start_command))
        dispatcher.add_handler(MessageHandler(PhotoFilter(), self.image_received))

        updater.start_polling()
        updater.idle()

    def start_command(self, update: Update, context: CallbackContext):
        update.message.reply_text('Bot started. Send an image to find similar products.')

    def image_received(self, update: Update, context: CallbackContext):
        global vectorizer, vectors, product_ids

        photo = update.message.photo[-1]
        image_file = context.bot.get_file(photo.file_id)
        image_data = image_file.download_as_bytearray()

        image = Image.open(BytesIO(image_data))
        processed_image = preprocess_image(image)

        scores = cosine_search(vectorizer, vectors, processed_image)

        n_closest = np.argsort(scores)[::-1][:5]
        closest_product_ids = product_ids[n_closest]

        from products.models import ProductModel

        products = ProductModel.objects.filter(id__in=closest_product_ids)

        for product in products:
            product_id = product.id
            title = product.title
            price = product.price
            url = product.url
            photo_data = product.photo

            context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_data)

            response = f"{title}\n<b>{price}</b>\n{url}\n\n"
            update.message.reply_html(response)
