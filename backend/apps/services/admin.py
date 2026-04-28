from django.contrib import admin
from .models import Category, Service, ComboItem

class ComboItemInline(admin.TabularInline):
    model = ComboItem
    fk_name = 'service'
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    ordering = ('order', 'name')
    search_fields = ('name',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'duration_minutes', 'base_price', 'is_combo', 'discount_strategy')
    list_filter = ('category', 'is_combo', 'discount_strategy')
    search_fields = ('name',)
    inlines = [ComboItemInline]
