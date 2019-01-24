from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Greeting message"

    def handle(self, *args, **options):
        self.stdout.write("Hello world")
