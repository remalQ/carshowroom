from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Car, Application
from django.contrib.auth.models import Group


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    search_fields = ('username',)
    ordering = ('username',)


class CarAdmin(admin.ModelAdmin):
    list_display = ['model', 'year', 'price', 'engine', 'slug']
    prepopulated_fields = {'slug': ('model', 'year')}  # Автозаполнение слага


admin.site.register(Car, CarAdmin)


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'created_at')
    list_filter = ('status', 'user')
    search_fields = ('title', 'description', 'user__username')


admin.site.register(Application, ApplicationAdmin)
