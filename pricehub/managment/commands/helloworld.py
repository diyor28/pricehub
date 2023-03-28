from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Hello world'

    def