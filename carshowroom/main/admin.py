from django.contrib import admin
from .models import Car


class CarAdmin(admin.ModelAdmin):
    list_display = ['model', 'year', 'price', 'engine', 'slug']
    prepopulated_fields = {'slug': ('model', 'year')}  # Автозаполнение слага


admin.site.register(Car, CarAdmin)
