import os

import csv
from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.constants import FILES
from recipes.models import Tag


class Command(BaseCommand):
    help = "Добавляет данные в модель Ingredient из .csv файлов в базу данных"

    def handle(self, *args, **options):
        dir = os.path.dirname(settings.BASE_DIR.parent)
        path = dir + FILES.get("tags")
        with open(
            file=path,
            mode="r",
            encoding="utf-8",
        ) as f:
            try:
                Tag.objects.bulk_create(
                    Tag(name=row[0], slug=row[1]) for row in csv.reader(f)
                )
                self.stdout.write(self.style.SUCCESS("Success"))
            except Exception as ex:
                self.stdout.write(self.style.ERROR(ex))
