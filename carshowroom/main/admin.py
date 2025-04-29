from django.contrib import admin
from .models import Car
from .models import Application


class CarAdmin(admin.ModelAdmin):
    list_display = ['model', 'year', 'price', 'engine', 'slug']
    prepopulated_fields = {'slug': ('model', 'year')}  # Автозаполнение слага


admin.site.register(Car, CarAdmin)


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'created_at')
    list_filter = ('status', 'user')
    search_fields = ('title', 'description', 'user__username')


admin.site.register(Application, ApplicationAdmin)