from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.contrib.auth.models import Group
from .forms import TradeInForm, CreditRequestForm, CarOrderForm, EmployeeRegistrationForm, \
    ClientSignUpForm, UserForm, CustomerForm, CustomUserRegistrationForm
from .models import TestDrive, Car, Employee, Client, Application
from django.contrib import messages


def index(request):
    featured_cars = Car.objects.all()[:3]  # Берем первые 3 автомобиля
    can_access_sales_dashboard = request.user.has_perm('sales.can_access_dashboard')

    context = {
        'can_access_sales_dashboard': can_access_sales_dashboard,
        'featured_cars': featured_cars,  # Передаем QuerySet вместо списка
        'special_offers': [
            {
                'title': 'Трейд-ин',
                'description': 'Повышенный выкуп вашего авто',
                'icon': 'fa-exchange-alt'
            },
            {
                'title': 'Кредит 1.9%',
                'description': 'Специальная программа кредитования',
                'icon': 'fa-percentage'
            }
        ]
    }
    return render(request, 'main/index.html', context)


def about(request):
    return render(request, 'main/about.html')


def contact(request):
    context = {
        'title': 'Контакты',
        'address': 'г. Москва, ул. Автозаводская, д. 23',
        'phone': '+7 (495) 123-45-67',
        'email': 'info@carshowroom.ru',
        'work_hours': 'Пн-Пт: 9:00 - 20:00, Сб-Вс: 10:00 - 18:00'
    }
    return render(request, 'main/contact.html', context)


def register_employee(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            employee_group, created = Group.objects.get_or_create(name='Сотрудники')
            user.groups.add(employee_group)
            return redirect('login')
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'main/register_employee.html', {'form': form})


@login_required
def redirect_view(request):
    if is_employee(request.user):
        return redirect('sales_employee')
    else:
        return redirect('profile')


def register_client(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login')
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'main/register_client.html', {'form': form})


def is_employee(user):
    return user.groups.filter(name='Менеджеры').exists()


@login_required
@user_passes_test(is_employee)
def change_application_status(request, application_id):
    application = get_object_or_404(Application, id=application_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Application.STATUS_CHOICES):
            application.status = new_status
            application.save()
            return redirect('sales_profile')  # Имя твоего профиля сотрудника

    return render(request, 'main/change_status.html', {
        'application': application,
        'status_choices': Application.STATUS_CHOICES,
    })


@login_required
def change_status(request, application_id):
    if not request.user.is_employee():
        return redirect('profile')

    app = get_object_or_404(Application, pk=application_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        app.status = new_status
        app.save()
        return redirect('profile')
    return render(request, 'main/change_status.html', {'app': app})


@login_required
def profile_view(request):
    user = request.user
    if user.is_employee():
        # Сотрудник видит все заявки
        applications = Application.objects.all()
        return render(request, 'main/sales_profile.html', {'applications': applications})
    else:
        # Клиент видит только свои заявки
        applications = Application.objects.filter(user=user)
        return render(request, 'main/profile.html', {'applications': applications})


# Представление для профиля сотрудника
@login_required
@user_passes_test(is_employee)
def sales_employee(request):
    try:
        # Пытаемся получить сотрудника по текущему пользователю
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        employee = None  # Если сотрудник не найден

    return render(request, 'main/sales_profile.html', {'employee': employee})


def car_order_view(request):
    if request.method == 'POST':
        form = CarOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            messages.success(request, 'Ваш заказ успешно оформлен!')
            return redirect('index')
    else:
        form = CarOrderForm()
    return render(request, 'main/car_order.html', {'form': form})


@login_required
def trade_in_request(request):
    if request.method == 'POST':
        form = TradeInForm(request.POST)
        if form.is_valid():
            trade_in = form.save(commit=False)
            trade_in.user = request.user  # привязываем заявку к текущему пользователю
            trade_in.save()
            return redirect('trade_in_success')  # перенаправление на страницу успеха
    else:
        form = TradeInForm()
    return render(request, 'main/trade_in_form.html', {'form': form})


def trade_in_success(request):
    return render(request, 'main/trade_in_success.html')


def car_detail(request, slug):
    car = get_object_or_404(Car, slug=slug)
    return render(request, 'main/car_detail.html', {'car': car})


def credit_info(request):
    if request.method == 'POST':
        form = CreditRequestForm(request.POST)
        if form.is_valid():
            credit_request = form.save(commit=False)
            credit_request.user = request.user  # Привязка заявки к текущему пользователю
            credit_request.save()
            return redirect('credit_thanks')  # Перенаправление на страницу благодарности
    else:
        form = CreditRequestForm()

    return render(request, 'main/credit_info.html', {'form': form})


def credit_thanks(request):
    return render(request, 'main/credit_thanks.html')


def sale_success(request):
    return render(request, 'main/sale_success.html')


def user_logout(request):
    logout(request)  # Выход из системы
    return redirect('/')  # Перенаправление на главную страницу
