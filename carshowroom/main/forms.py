from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CarOrder, CustomUser, TradeInRequest, CreditRequest, Application, Car
from django.contrib.contenttypes.models import ContentType

STATUS_CHOICES = [
    ('pending', 'В ожидании'),
    ('approved', 'Одобрено'),
    ('rejected', 'Отклонено'),
    ('in_progress', 'В процессе'),
]


class TradeInStatusForm(forms.ModelForm):
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = TradeInRequest
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class CarOrderStatusForm(forms.ModelForm):
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = CarOrder
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class CreditStatusForm(forms.ModelForm):
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = CreditRequest
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


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


class TradeInCreateForm(forms.ModelForm):
    class Meta:
        model = TradeInRequest
        exclude = ['user', 'created_at', 'status']
        widgets = {
            'current_car_brand': forms.TextInput(attrs={'class': 'form-control'}),
            'current_car_model': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'mileage': forms.NumberInput(attrs={'class': 'form-control'}),
            'desired_car': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control'}),
        }


class CarOrderCreateForm(forms.ModelForm):
    class Meta:
        model = CarOrder
        exclude = ['user', 'order_date', 'status']
        widgets = {
            'car': forms.Select(attrs={'class': 'form-select'}),
        }


class CreditCreateForm(forms.ModelForm):
    class Meta:
        model = CreditRequest
        exclude = ['user', 'status', 'created_at']
        widgets = {
            'car': forms.Select(attrs={'class': 'form-select'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'}),
        }
