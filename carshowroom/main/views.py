from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group
from .forms import TradeInForm, CreditRequestForm, CarOrderForm, CustomUserRegistrationForm, UserProfileForm, \
    ApplicationForm, ApplicationStatusForm, ChangeStatusForm
from .models import Car, Employee, Application, TradeInRequest, CreditRequest, CarOrder
from django.contrib import messages


@login_required
def create_application(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user  # Привязываем заявку к текущему пользователю
            application.save()
            messages.success(request, 'Заявка успешно отправлена!')
            return redirect('some_success_url')
    else:
        form = ApplicationForm()

    return render(request, 'main/application_form.html', {'form': form})


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
def change_status(request, application_type, application_id):
    # Determine the application type and get the respective model object
    if application_type == 'tradein':
        application_obj = get_object_or_404(TradeInRequest, id=application_id)
    elif application_type == 'purchase':
        application_obj = get_object_or_404(CarOrder, id=application_id)
    elif application_type == 'credit':
        application_obj = get_object_or_404(CreditRequest, id=application_id)
    else:
        # Handle invalid application type, e.g., 404 or redirect
        return redirect('sales_employee')

    # Initialize the form with the application instance
    if request.method == 'POST':
        form = ChangeStatusForm(request.POST, instance=application_obj)
        if form.is_valid():
            form.save()  # Save the updated status
            return redirect('sales_employee')  # Redirect to the sales employee page
    else:
        form = ChangeStatusForm(instance=application_obj)

    context = {
        'form': form,
        'application_type': application_type,
        'application_obj': application_obj
    }

    return render(request, 'main/change_status.html', context)


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Перенаправляем на профиль после сохранения изменений
    else:
        form = UserProfileForm(instance=request.user)

    # Пагинация для заявок
    tradein_requests = TradeInRequest.objects.filter(user=request.user)
    paginator = Paginator(tradein_requests, 5)  # Показывать по 5 заявок на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    purchase_requests = CarOrder.objects.filter(user=request.user)
    purchase_paginator = Paginator(purchase_requests, 5)
    purchase_page_obj = purchase_paginator.get_page(page_number)

    credit_requests = CreditRequest.objects.filter(user=request.user)
    credit_paginator = Paginator(credit_requests, 5)
    credit_page_obj = credit_paginator.get_page(page_number)

    return render(request, 'main/profile.html', {
        'form': form,
        'page_obj': page_obj,
        'purchase_page_obj': purchase_page_obj,
        'credit_page_obj': credit_page_obj,
    })


@login_required
def user_requests_view(request):
    user = request.user
    context = {
        'car_orders': CarOrder.objects.filter(user=user),
        'trade_ins': TradeInRequest.objects.filter(user=user),
        'credit_requests': CreditRequest.objects.filter(user=user),
    }
    return render(request, 'user_requests.html', context)


# Представление для профиля сотрудника
@login_required
@user_passes_test(is_employee)
def sales_employee(request):
    try:
        # Пытаемся получить сотрудника по текущему пользователю
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        employee = None  # Если сотрудник не найден

    # Пагинация для всех заявок
    tradein_requests = TradeInRequest.objects.all()  # Показываем заявки всех пользователей
    paginator = Paginator(tradein_requests, 5)  # Показывать по 5 заявок на страницу
    page_number = request.GET.get('page')
    tradein_page_obj = paginator.get_page(page_number)

    purchase_requests = CarOrder.objects.all()
    purchase_paginator = Paginator(purchase_requests, 5)
    purchase_page_obj = purchase_paginator.get_page(page_number)

    credit_requests = CreditRequest.objects.all()
    credit_paginator = Paginator(credit_requests, 5)
    credit_page_obj = credit_paginator.get_page(page_number)

    # Теперь мы передаем статус заявки в контекст для отображения
    return render(request, 'main/sales_profile.html', {
        'employee': employee,
        'tradein_page_obj': tradein_page_obj,
        'purchase_page_obj': purchase_page_obj,
        'credit_page_obj': credit_page_obj,
    })


@login_required
def car_order_view(request):
    if request.method == 'POST':
        form = CarOrderForm(request.POST)
        if form.is_valid():
            # Создаем заявку
            application = form.save(commit=False)
            application.user = request.user

            # Привязка заявки к соответствующему объекту (Car, TradeInRequest, или CreditRequest)
            car = form.cleaned_data.get('car')
            trade_in = form.cleaned_data.get('trade_in')
            credit_request = form.cleaned_data.get('credit_request')

            if car:
                # Получаем ContentType для Car и связываем заявку
                content_type = ContentType.objects.get_for_model(Car)
                application.content_type = content_type
                application.object_id = car.id
            elif trade_in:
                # Получаем ContentType для TradeInRequest и связываем заявку
                content_type = ContentType.objects.get_for_model(TradeInRequest)
                application.content_type = content_type
                application.object_id = trade_in.id
            elif credit_request:
                # Получаем ContentType для CreditRequest и связываем заявку
                content_type = ContentType.objects.get_for_model(CreditRequest)
                application.content_type = content_type
                application.object_id = credit_request.id

            application.save()
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
            trade_in.user = request.user  # Привязываем заявку к текущему пользователю
            trade_in.save()  # Сохраняем заявку

            # Создаем заявку типа "trade_in" в модели Application
            application = Application.objects.create(
                user=request.user,
                content_type=ContentType.objects.get_for_model(TradeInRequest),
                object_id=trade_in.id,
                status='pending',  # Статус по умолчанию
            )

            return redirect('trade_in_success')  # Перенаправление на страницу успеха
    else:
        form = TradeInForm()

    return render(request, 'main/trade_in_form.html', {'form': form})


def trade_in_success(request):
    return render(request, 'main/trade_in_success.html')


def car_detail(request, slug):
    car = get_object_or_404(Car, slug=slug)
    return render(request, 'main/car_detail.html', {'car': car})


@login_required
def credit_info(request):
    if request.method == 'POST':
        form = CreditRequestForm(request.POST)
        if form.is_valid():
            credit_request = form.save(commit=False)
            credit_request.user = request.user  # Привязываем заявку к текущему пользователю
            credit_request.save()  # Сохраняем кредитную заявку

            # Создаем заявку типа 'credit_request' в модели Application
            application = Application.objects.create(
                user=request.user,
                content_type=ContentType.objects.get_for_model(CreditRequest),  # Указываем тип объекта как CreditRequest
                object_id=credit_request.id,  # ID этой заявки
                status='pending',  # Статус по умолчанию
            )

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
