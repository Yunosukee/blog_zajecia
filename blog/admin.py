from django.contrib import admin
from .models import Product, Category, DiscountCode, Order

class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'get_discount_display', 'is_active', 'times_used', 'uses_limit', 'valid_until')
    list_filter = ('discount_type', 'is_active', 'created_at')
    search_fields = ('code', 'description')
    readonly_fields = ('times_used', 'created_at', 'updated_at')
    fieldsets = (
        ('Informacje o kodzie', {
            'fields': ('code', 'description', 'is_active')
        }),
        ('Rabat', {
            'fields': ('discount_type', 'discount_value', 'min_order_value')
        }),
        ('Ograniczenia', {
            'fields': ('valid_from', 'valid_until', 'uses_limit', 'times_used')
        }),
        ('Metadane', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_discount_display(self, obj):
        return f"{obj.discount_value}{'%' if obj.discount_type == 'percent' else 'z\u0142'}"
    get_discount_display.short_description = "Rabat"


class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'final_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'blik_code')
    readonly_fields = ('order_number', 'products', 'created_at', 'paid_at')
    fieldsets = (
        ('Informacje o zam\u00f3wieniu', {
            'fields': ('order_number', 'status', 'created_at', 'paid_at')
        }),
        ('Produkty i ceny', {
            'fields': ('products', 'total_price', 'discount_amount', 'final_price', 'discount_code')
        }),
        ('P\u0142atno\u015b\u0107', {
            'fields': ('blik_code',)
        }),
    )

# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(DiscountCode, DiscountCodeAdmin)
admin.site.register(Order, OrderAdmin)