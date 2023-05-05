import csv

from django.core.management import BaseCommand
from foodgram.settings import BASE_DIR
from recipes.models import Ingredient, Tag

TABLES = {
    Ingredient: 'ingredients.csv',
    Tag: 'tags.csv'
}

CSV_FILE_PATH = BASE_DIR / 'data'


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        for model, csv_f in TABLES.items():
            with open(
                    CSV_FILE_PATH / csv_f, encoding='utf-8'
            ) as csv_file:
                for record in csv.DictReader(csv_file):
                    model.objects.get_or_create(**record)
        self.stdout.write(
            self.style.SUCCESS('Success write to database'))
