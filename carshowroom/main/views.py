from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm, RegisterForm
from .models import TestDrive
from .forms import CarOrderForm, TradeInForm
from django.contrib import messages
from .models import Car


def index(request):
    featured_cars = Car.objects.all()[:3]  # Берем первые 3 автомобиля

    context = {
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
            # Автоматический вход после регистрации
            from django.contrib.auth import login
            login(request, user)
            return redirect('profile')
    else:
        form = RegisterForm()
    return render(request, 'main/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)

    context = {
        'user': request.user,
        'form': form,
        'test_drives': TestDrive.objects.filter(user=request.user),
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


def tradein_request_view(request):
    if request.method == 'POST':
        form = TradeInForm(request.POST)
        if form.is_valid():
            tradein = form.save(commit=False)
            tradein.user = request.user
            tradein.save()
            messages.success(request, 'Заявка на трейд-ин отправлена!')
            return redirect('index')
    else:
        form = TradeInForm()
    return render(request, 'main/tradein_request.html', {'form': form})


def car_detail(request, slug):
    car = get_object_or_404(Car, slug=slug)
    return render(request, 'main/car_detail.html', {'car': car})
