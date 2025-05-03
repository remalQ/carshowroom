from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CarOrder, CustomUser, TradeInRequest, CreditRequest, Application, Car
from django.contrib.contenttypes.models import ContentType


class ChangeStatusForm(forms.ModelForm):
    # Define the choices for status
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
        ('in_progress', 'В процессе'),
        # Add other statuses if necessary
    ]

    # Create a status field for the form
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = None  # Model will be dynamically assigned later
        fields = ['status']

    def __init__(self, *args, **kwargs):
        # Dynamically set the model based on the request object
        request_obj = kwargs.get('instance')

        if isinstance(request_obj, TradeInRequest):
            self.Meta.model = TradeInRequest
        elif isinstance(request_obj, CarOrder):
            self.Meta.model = CarOrder
        elif isinstance(request_obj, CreditRequest):
            self.Meta.model = CreditRequest
        else:
            raise ValueError("Unknown application type")

    def save(self, commit=True):
        # Ensure the form saves the new status to the model instance
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance


class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['status']


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['status']  # Только поле статуса в форме, другие поля добавляются динамически

    car = forms.ModelChoiceField(queryset=Car.objects.all(), required=False)
    trade_in = forms.ModelChoiceField(queryset=TradeInRequest.objects.all(), required=False)
    credit_request = forms.ModelChoiceField(queryset=CreditRequest.objects.all(), required=False)

    def clean(self):
        cleaned_data = super().clean()
        car = cleaned_data.get("car")
        trade_in = cleaned_data.get("trade_in")
        credit_request = cleaned_data.get("credit_request")

        if not (car or trade_in or credit_request):
            raise forms.ValidationError("Вы должны выбрать хотя бы один объект (автомобиль, заявку на обмен или заявку на кредит).")

        # Привязываем соответствующий ContentType и object_id
        if car:
            self.instance.content_type = ContentType.objects.get_for_model(Car)
            self.instance.object_id = car.id
        elif trade_in:
            self.instance.content_type = ContentType.objects.get_for_model(TradeInRequest)
            self.instance.object_id = trade_in.id
        elif credit_request:
            self.instance.content_type = ContentType.objects.get_for_model(CreditRequest)
            self.instance.object_id = credit_request.id

        return cleaned_data


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class CustomUserRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username',)

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class CarOrderForm(forms.ModelForm):
    class Meta:
        model = CarOrder
        fields = ['car']
        widgets = {
            'car': forms.Select(attrs={'class': 'form-control'}),
        }


class TradeInForm(forms.ModelForm):
    class Meta:
        model = TradeInRequest
        fields = ['current_car_brand', 'current_car_model', 'year', 'mileage', 'desired_car', 'phone', 'email', 'comment']


class CreditRequestForm(forms.ModelForm):
    class Meta:
        model = CreditRequest
        fields = ['car', 'full_name', 'phone', 'email', 'amount', 'duration']
