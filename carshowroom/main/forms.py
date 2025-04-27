from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import CarOrder, TradeInRequest, CreditRequest, SaleContract, CarConfiguration, SalesEmployee


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
        fields = ['department']


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})


class CarOrderForm(forms.ModelForm):
    class Meta:
        model = CarOrder
        fields = ['car', 'status', 'comment', 'phone']


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
