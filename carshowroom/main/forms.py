from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CarOrder, CustomUser, TradeInRequest, CreditRequest, SaleContract, CarConfiguration, \
    Employee, Client, Customer


class EmployeeRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    position = forms.CharField(required=False)
    department = forms.ChoiceField(choices=Employee.DEPARTMENT_CHOICES)
    hire_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2',
                  'position', 'department', 'hire_date']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email  # на всякий случай
        user.is_employee = True
        if commit:
            user.save()
            # Создаём профиль сотрудника
            Employee.objects.create(
                user=user,
                position=self.cleaned_data.get('position'),
                department=self.cleaned_data.get('department'),
                hire_date=self.cleaned_data.get('hire_date'),
            )
        return user


class ClientSignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_client = True
        if commit:
            user.save()
            Client.objects.create(user=user)
        return user


class UserForm(UserChangeForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email']


class CustomerForm(forms.ModelForm):
    phone = forms.CharField(max_length=20, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Customer
        fields = ['phone', 'address']


class CarOrderStatusForm(forms.ModelForm):
    class Meta:
        model = CarOrder
        fields = ['status']
        widgets = {
            'status': forms.Select(choices=CarOrder.STATUS_CHOICES),
        }


class CarOrderForm(forms.ModelForm):
    class Meta:
        model = CarOrder
        fields = ['car_model']
        widgets = {
            'car_model': forms.Select(attrs={'class': 'form-control'}),
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
