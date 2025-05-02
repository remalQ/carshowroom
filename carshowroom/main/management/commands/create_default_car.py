from django.core.management.base import BaseCommand
from django.utils.text import slugify
from ...models import Car


class Command(BaseCommand):
    help = 'Создаёт дефолтный автомобиль, если он ещё не существует'

    def handle(self, *args, **options):
        slug = slugify("Default Model 2020")
        car, created = Car.objects.get_or_create(
            slug=slug,
            defaults={
                'model': 'Default Model',
                'year': 2020,
                'engine': '1.6L',
                'price': 1000000,
                'image': 'cars/default.jpg',
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'✅ Автомобиль "{car}" успешно создан.'))
        else:
            self.stdout.write(self.style.WARNING(f'ℹ️ Автомобиль "{car}" уже существует.'))
