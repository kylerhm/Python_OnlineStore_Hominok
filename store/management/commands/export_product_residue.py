from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.apps import apps


class Command(BaseCommand):
    help = "Экспорт остатков товаров в JSON файл"

    def handle(self, *args, **options):
        # Экспортируем данные моделей Product
        call_command("dumpdata", "store.product", indent=2, use_natural_primary_key=False)

        self.stdout.write(
            self.style.SUCCESS("Данные экспортированы в стандартный вывод")
        )
