import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.constants import FILES
from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Добавляет данные в модель Ingredient из .csv файлов в базу данных"

    def handle(self, *args, **options):
        path = os.path.dirname(settings.BASE_DIR) + FILES.get("ingredients")
        with open(
            file=path,
            mode="r",
            encoding="utf-8",
        ) as f:
            try:
                Ingredient.objects.bulk_create(
                    Ingredient(name=row[0], measurement_unit=row[1])
                    for row in csv.reader(f)
                )
                self.stdout.write(self.style.SUCCESS("Success"))
            except Exception as ex:
                self.stdout.write(self.style.ERROR(ex))
