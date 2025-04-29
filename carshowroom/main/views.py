from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.exceptions import PermissionDenied
from .forms import ProfileForm, RegisterForm, TradeInForm, CreditRequestForm, \
    UsedCarSaleForm, CarConfigurationForm, SalesEmployeeForm, CustomerForm, CarOrderStatusForm
from .models import TestDrive, Car, SaleContract, SalesEmployee, CarOrder, CreditRequest, TradeInRequest, \
    Customer, Application
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


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            from django.contrib.auth import login
            login(request, user)

            # Создаем профиль Customer для нового пользователя
            Customer.objects.create(
                user=user,
                phone=form.cleaned_data.get('phone', '')  # если добавили phone в RegisterForm
            )

            if SalesEmployee.objects.filter(user=user).exists():
                return redirect('sales_profile')
            else:
                return redirect('profile')
    else:
        form = RegisterForm()
    return render(request, 'main/register.html', {'form': form})


@login_required
def sales_employee_profile(request):
    try:
        employee = request.user.employee

        # Получаем все заявки (например, CarOrder)
        orders = CarOrder.objects.all()

        if request.method == 'POST':
            user_form = ProfileForm(request.POST, instance=request.user)
            employee_form = SalesEmployeeForm(request.POST, instance=employee)

            # Если форма статуса заявки отправлена, обновляем статус заявки
            if 'status_form' in request.POST:
                status_form = CarOrderStatusForm(request.POST)
                if status_form.is_valid():
                    status_form.save()
                    messages.success(request, 'Статус заявки обновлен.')
                    return redirect('sales_profile')
            else:
                status_form = CarOrderStatusForm()

            if user_form.is_valid() and employee_form.is_valid():
                user_form.save()
                employee_form.save()
                messages.success(request, 'Профиль сотрудника успешно обновлен.')
                return redirect('sales_profile')
        else:
            user_form = ProfileForm(instance=request.user)
            employee_form = SalesEmployeeForm(instance=employee)
            status_form = CarOrderStatusForm()

        context = {
            'user_form': user_form,
            'employee_form': employee_form,
            'employee': employee,
            'orders': orders,  # Передаем все заявки
            'status_form': status_form,  # Форма для изменения статуса
        }
        return render(request, 'main/sales_profile.html', context)

    except SalesEmployee.DoesNotExist:
        return redirect('profile')


@login_required
def redirect_user(request):
    if hasattr(request.user, 'employee'):  # Проверяем, является ли пользователь сотрудником
        return redirect('sales_employee_profile')
    else:
        return redirect('profile')


@login_required
def profile(request):
    try:
        customer = request.user.customer
    except AttributeError:
        customer = Customer.objects.create(user=request.user)

    if request.method == 'POST':
        user_form = ProfileForm(request.POST, instance=request.user)
        customer_form = CustomerForm(request.POST, instance=customer)

        if user_form.is_valid() and customer_form.is_valid():
            user_form.save()
            customer_form.save()
            messages.success(request, 'Профиль успешно обновлен.')
            return redirect('profile')
    else:
        user_form = ProfileForm(instance=request.user)
        customer_form = CustomerForm(instance=customer)

    orders = CarOrder.objects.filter(user=request.user)
    test_drives = TestDrive.objects.filter(user=request.user)
    trade_in_requests = TradeInRequest.objects.filter(user=request.user)
    credit_requests = CreditRequest.objects.filter(user=request.user)

    context = {
        'user_form': user_form,
        'customer_form': customer_form,
        'customer': customer,
        'orders': orders,
        'test_drives': test_drives,
        'trade_in_requests': trade_in_requests,
        'credit_requests': credit_requests,
    }
    return render(request, 'main/profile.html', context)


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


@login_required
def used_car_sale(request):
    if request.method == 'POST':
        form = UsedCarSaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            sale.user = request.user
            # Получаем сотрудника, который оформляет сделку
            employee = SalesEmployee.objects.get(user=request.user)
            sale.sales_employee = employee  # Привязываем сотрудника
            sale.sale_type = 'used'
            sale.save()
            messages.success(request, 'Автомобиль с пробегом продан!')
            return redirect('sale_success')
    else:
        form = UsedCarSaleForm()

    return render(request, 'main/used_car_sale.html', {'form': form})


@login_required
def new_car_sale(request):
    if request.method == 'POST':
        form = CarConfigurationForm(request.POST)
        if form.is_valid():
            config = form.save(commit=False)
            config.save()

            # Получаем сотрудника, который оформляет сделку
            employee = SalesEmployee.objects.get(user=request.user)

            sale = SaleContract.objects.create(
                car=config.car,
                user=request.user,
                sale_price=config.price,
                sale_type='new',
                sales_employee=employee  # Привязка сотрудника
            )
            messages.success(request, 'Новый автомобиль продан!')
            return redirect('sale_success')
    else:
        form = CarConfigurationForm()

    return render(request, 'main/new_car_sale.html', {'form': form})


def sale_success(request):
    return render(request, 'main/sale_success.html')


@login_required
def sales_employee_profile(request):
    try:
        employee = SalesEmployee.objects.get(user=request.user)
    except SalesEmployee.DoesNotExist:
        raise PermissionDenied  # Если сотрудник не найден, можно перенаправить на страницу ошибки

    if request.method == 'POST':
        form = SalesEmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('sales_employee_profile')  # Перенаправление после сохранения
    else:
        form = SalesEmployeeForm(instance=employee)

    context = {
        'form': form,
        'employee': employee,
    }
    return render(request, 'main/sales_employee_profile.html', context)


def user_logout(request):
    logout(request)  # Выход из системы
    return redirect('/')  # Перенаправление на главную страницу