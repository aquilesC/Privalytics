from django.core.management import BaseCommand
from django.template.loader import render_to_string


class Command(BaseCommand):
    help = """Creates a static index file
    """

    def handle(self, *args, **options):
        txt = render_to_string('privalytics/index.html')
        with open('index.html', 'w') as f:
            f.write(txt)