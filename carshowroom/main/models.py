from django.db import models
from django.contrib.auth.models import User, Permission
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Связь с покупателем
    car = models.ForeignKey(Car, on_delete=models.CASCADE)  # Связь с автомобилем
    order_date = models.DateTimeField(auto_now_add=True)  # Дата заказа
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Ожидает'),
        ('confirmed', 'Подтверждён'),
        ('delivered', 'Доставлен'),
    ], default='pending')  # Статус заказа
    comment = models.TextField(null=True, blank=True)  # Комментарий к заказу
    phone = models.CharField(max_length=20)  # Телефон клиента

    def __str__(self):
        return f'Заказ {self.car.model} для {self.user.get_full_name()}'


# Модель для заявки на трейд-ин (TradeInRequest)
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


# Модель для заявки на кредит (CreditRequest)
class CreditRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)  # Сумма кредита
    duration = models.PositiveIntegerField()  # Срок кредита в месяцах
    status = models.CharField(max_length=50, choices=[('pending', 'В обработке'), ('approved', 'Одобрено'), ('rejected', 'Отклонено')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Кредитная заявка для {self.car.model} от {self.full_name}"


class CreditRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)  # Сумма кредита
    duration = models.PositiveIntegerField()  # Срок кредита в месяцах
    status = models.CharField(max_length=50, choices=[('pending', 'В обработке'), ('approved', 'Одобрено'), ('rejected', 'Отклонено')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Кредитная заявка для {self.car.model} от {self.full_name}"


class UsedCar(models.Model):
    car = models.OneToOneField(Car, on_delete=models.CASCADE)
    mileage = models.PositiveIntegerField()  # Пробег в километрах
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Цена с пробегом
    sold = models.BooleanField(default=False)  # Флаг продажи
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.car.model} - {self.mileage} км"


class CarConfiguration(models.Model):
    car = models.OneToOneField(Car, on_delete=models.CASCADE)
    color = models.CharField(max_length=50)
    engine_type = models.CharField(max_length=50)
    interior = models.CharField(max_length=100)  # Внутренний интерьер (цвет сидений, отделка)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Цена комплектации
    available = models.BooleanField(default=True)  # Доступность комплектации

    def __str__(self):
        return f"{self.car.model} - {self.color}, {self.engine_type}"


class SalesEmployee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100, default="Отдел продаж")
    hired_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.department}"

    def sales_dashboard_permission(user):
        return SalesEmployee.objects.filter(user=user).exists()


class SaleContract(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sales_employee = models.ForeignKey(SalesEmployee, on_delete=models.SET_NULL, null=True, blank=True)  # Сотрудник, который оформил продажу
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    contract_date = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    sale_type = models.CharField(max_length=50, choices=[('used', 'Авто с пробегом'), ('new', 'Новое авто')])

    def __str__(self):
        return f"Договор продажи {self.car.model} - {self.user.username}"