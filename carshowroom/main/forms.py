from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import CarOrder, TradeInRequest, CreditRequest, SaleContract, CarConfiguration, SalesEmployee, Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['phone', 'address']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class SalesEmployeeForm(forms.ModelForm):
    class Meta:
        model = SalesEmployee
        fields = ['position', 'hire_date']
        widgets = {
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'hire_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})


class CarOrderStatusForm(forms.ModelForm):
    class Meta:
        model = CarOrder
        fields = ['status']
        widgets = {
            'status': forms.Select(choices=CarOrder.STATUS_CHOICES),
        }


class TradeInForm(forms.ModelForm):
    class Meta:
        model = TradeInRequest
        fields = ['current_car_brand', 'current_car_model', 'year', 'mileage', 'desired_car', 'phone', 'email', 'comment']


class CreditRequestForm(forms.ModelForm):
    class Meta:
        model = CreditRequest
        fields = ['car', 'full_name', 'phone', 'email', 'amount', 'duration']


class UsedCarSaleForm(forms.ModelForm):
    class Meta:
        model = SaleContract
        fields = ['car', 'sale_price', 'sale_type']


class CarConfigurationForm(forms.ModelForm):
    class Meta:
        model = CarConfiguration
        fields = ['car', 'color', 'engine_type', 'interior', 'price', 'available']
