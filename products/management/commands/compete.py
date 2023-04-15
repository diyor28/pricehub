import queue
import time
from threading import Thread

from django.core.management import BaseCommand

from pricehub.products import timeit

paint_running = True


def paint_gorshki(gorshki_q, sklad_q):
    while True:
        time.sleep(0.5)
        if not paint_running:
            break
        gorshok = gorshki_q.get()
        print(f"Painted gorshok #{gorshok}")
        sklad_q.put(gorshok)


def make_gorshki(glina_q, gorshki_q):
    global paint_running

    while True:
        time.sleep(0.5)
        if glina_q.empty():
            paint_running = False
            break
        gorshok = glina_q.get()
        print(f"Made gorshok #{gorshok}")
        gorshki_q.put(gorshok)


class Command(BaseCommand):
    help = 'Downloads categories from API'

    @timeit
    def handle(self, *args, **options):
        gonchari = []
        painters = []
        glina_q = queue.Queue(150)
        gorshki_q = queue.Queue(150)
        sklad_q = queue.Queue(150)

        for i in range(100):
            glina_q.put(i)

        for i in range(10):
            th = Thread(target=make_gorshki, args=(glina_q, gorshki_q))
            th.start()
            gonchari.append(th)

        for i in range(10):
            th = Thread(target=paint_gorshki, args=(gorshki_q, sklad_q))
            th.start()
            painters.append(th)

        results = []
        while len(results) < 100:
            results.append(sklad_q.get())

        for th in gonchari:
            th.join()

        for th in painters:
            th.join()
