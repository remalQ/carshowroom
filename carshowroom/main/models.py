from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth.models import BaseUserManager
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


STATUS_CHOICES = (
    ('new', 'Новая'),
    ('in_progress', 'В обработке'),
    ('completed', 'Завершена'),
    ('rejected', 'Отклонена'),
)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class Car(models.Model):
    model = models.CharField(max_length=100, verbose_name="Модель")
    year = models.PositiveIntegerField(verbose_name="Год выпуска")
    engine = models.CharField(max_length=50, verbose_name="Двигатель")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to='cars/', verbose_name="Изображение", blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, db_index=True, verbose_name="Слаг")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.model}-{self.year}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.model} ({self.year})"

    class Meta:
        permissions = [
            ('view_all_orders', 'Can view all car orders'),
        ]


class CarOrder(models.Model):
    STATUS_CHOICES = STATUS_CHOICES

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    car = models.ForeignKey('Car', on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    def __str__(self):
        return f"Заказ {self.car} — {self.get_status_display()}"

    class Meta:
        ordering = ['-order_date']


# Модель для заявки на трейд-ин (TradeInRequest)
class TradeInRequest(models.Model):
    STATUS_CHOICES = STATUS_CHOICES

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    current_car_brand = models.CharField(max_length=255)
    current_car_model = models.CharField(max_length=255)
    year = models.PositiveIntegerField()
    mileage = models.PositiveIntegerField()
    desired_car = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Trade-In: {self.current_car_brand} {self.current_car_model} ({self.get_status_display()})"

    class Meta:
        ordering = ['-created_at']


# Модель для заявки на кредит (CreditRequest)
class CreditRequest(models.Model):
    STATUS_CHOICES = STATUS_CHOICES

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    car = models.ForeignKey('Car', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    duration = models.PositiveIntegerField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Кредит: {self.car} — {self.amount}₽ на {self.duration} мес. ({self.get_status_display()})"

    class Meta:
        ordering = ['-created_at']


class CarConfiguration(models.Model):
    car = models.OneToOneField(Car, on_delete=models.CASCADE)
    color = models.CharField(max_length=50)
    engine_type = models.CharField(max_length=50)
    interior = models.CharField(max_length=100)  # Внутренний интерьер (цвет сидений, отделка)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Цена комплектации
    available = models.BooleanField(default=True)  # Доступность комплектации

    def __str__(self):
        return f"{self.car.model} - {self.color}, {self.engine_type}"


class CustomUser(AbstractUser):
    def is_employee(self):
        return self.groups.filter(name="Менеджеры").exists()

    def is_client(self):
        return not self.is_employee()


# Модель клиента
class Client(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Клиент: {self.user.get_full_name() or self.user.email}"


# Модель сотрудника
class Employee(models.Model):
    DEPARTMENT_CHOICES = [
        ('sales', 'Отдел продаж'),
        ('service', 'Сервис'),
        ('admin', 'Администрация'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Связь с CustomUser
    position = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES, default='sales')
    hire_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Сотрудник: {self.user.get_full_name() or self.user.email}"


class Application(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = STATUS_CHOICES

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.content_type} #{self.object_id} ({self.status})"

    def title(self):
        return str(self.content_object)
