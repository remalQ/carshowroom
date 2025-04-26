from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Car(models.Model):
    model = models.CharField(max_length=100, verbose_name="Модель")
    year = models.PositiveIntegerField(verbose_name="Год выпуска")
    engine = models.CharField(max_length=50, verbose_name="Двигатель")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to='cars/', verbose_name="Изображение")
    slug = models.SlugField(unique=True, blank=True, db_index=True, verbose_name="Слаг")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.model}-{self.year}")  # Генерация слага на основе модели и года
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.model} ({self.year})"


class TestDrive(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтвержден'),
        ('completed', 'Завершен'),
        ('canceled', 'Отменен'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey('Car', on_delete=models.CASCADE)
    date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def get_status_class(self):
        return {
            'pending': 'warning',
            'confirmed': 'success',
            'completed': 'info',
            'canceled': 'danger',
        }.get(self.status, 'secondary')


class CarOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car_model = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[('pending', 'В обработке'), ('confirmed', 'Подтверждено'), ('rejected', 'Отклонено')], default='pending')

    def __str__(self):
        return f"Заказ {self.car_model} от {self.full_name}"


class TradeInRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    current_car_brand = models.CharField(max_length=255)
    current_car_model = models.CharField(max_length=255)
    year = models.PositiveIntegerField()
    mileage = models.PositiveIntegerField()
    desired_car = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[('pending', 'В обработке'), ('contacted', 'Связались')], default='pending')

    def __str__(self):
        return f"Трейд-ин {self.current_car_brand} {self.current_car_model}"