from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('order/', views.car_order_view, name='car_order'),
    path('trade-in/', views.trade_in_request, name='trade_in'),
    path('trade-in/success/', views.trade_in_success, name='trade_in_success'),
    path('car/<slug:slug>/', views.car_detail, name='car_detail'),
    path('credit/', views.credit_info, name='credit'),
    path('credit-thanks/', views.credit_thanks, name='credit_thanks'),
    path('used_car_sale/', views.used_car_sale, name='used_car_sale'),
    path('new_car_sale/', views.new_car_sale, name='new_car_sale'),
    path('sale_success/', views.sale_success, name='sale_success'),
    path('profile/', views.profile, name='profile'),
    path('sales_employee/', views.sales_employee_profile, name='sales_employee'),
    path('', views.redirect_user, name='redirect_user'),
]
