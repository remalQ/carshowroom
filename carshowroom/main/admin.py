from django.contrib import admin
from .models import Car
from .models import Application
from .models import CustomUser, ClientStatusFilter, EmployeeStatusFilter
from .models import Client, Employee, Customer


class CustomerInline(admin.StackedInline):
    model = Customer
    can_delete = False
    extra = 0


class ClientInline(admin.StackedInline):
    model = Client
    can_delete = False
    extra = 0


class EmployeeInline(admin.StackedInline):
    model = Employee
    can_delete = False
    extra = 0


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_staff', 'is_superuser', 'is_client', 'is_employee')
    search_fields = ('email',)
    list_filter = ('is_staff', 'is_superuser', ClientStatusFilter, EmployeeStatusFilter)
    inlines = [CustomerInline, ClientInline, EmployeeInline]


admin.site.register(CustomUser, CustomUserAdmin)


class CarAdmin(admin.ModelAdmin):
    list_display = ['model', 'year', 'price', 'engine', 'slug']
    prepopulated_fields = {'slug': ('model', 'year')}  # Автозаполнение слага


admin.site.register(Car, CarAdmin)


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'created_at')
    list_filter = ('status', 'user')
    search_fields = ('title', 'description', 'user__username')


admin.site.register(Application, ApplicationAdmin)
