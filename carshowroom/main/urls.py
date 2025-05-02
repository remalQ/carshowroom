from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('redirect/', views.redirect_view, name='redirect'),
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('order/', views.car_order_view, name='car_order'),
    path('trade-in/', views.trade_in_request, name='trade_in'),
    path('trade-in/success/', views.trade_in_success, name='trade_in_success'),
    path('car/<slug:slug>/', views.car_detail, name='car_detail'),
    path('credit/', views.credit_info, name='credit'),
    path('credit-thanks/', views.credit_thanks, name='credit_thanks'),
    path('sale_success/', views.sale_success, name='sale_success'),
    path('register/client/', views.register_client, name='register_client'),
    path('register/employee/', views.register_employee, name='register_employee'),
    path('profile/', views.profile_view, name='profile'),
    path('sales_employee/', views.sales_employee, name='sales_employee'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('application/<int:application_id>/change_status/', views.change_application_status, name='change_application_status'),
    path('my-requests/', views.user_requests_view, name='user_requests'),
]
