import json
from django.core.management.base import BaseCommand
from django.core.management import call_command
from store.models import Product


class Command(BaseCommand):
    help = "Импорт товаров из JSON файла"

    def add_arguments(self, parser):
        parser.add_argument(
            "filename",
            type=str,
            help="Путь к JSON файлу с данными товаров",
        )

    def handle(self, *args, **options):
        filename = options["filename"]

        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Файл '{filename}' не найден"))
            return
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR("Ошибка чтения JSON файла"))
            return

        created_count = 0
        for item in data:
            Product.objects.update_or_create(
                pk=item.get("id"),
                defaults={
                    "name": item.get("name", ""),
                    "description": item.get("description", ""),
                    "price": item.get("price", 0),
                    "stock_quantity": item.get("stock_quantity", 0),
                },
            )
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Успешно импортировано {created_count} товаров из {filename}")
        )
