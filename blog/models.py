from django.db import models
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='products/')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    stock = models.IntegerField(default=0)  # Stan magazynowy
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def short_description(self):
        words = self.description.split()
        if len(words) > 50:
            return ' '.join(words[:30]) + '...'
        else:
            return self.description
    
    def is_in_stock(self):
        return self.stock > 0


class DiscountCode(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percent', 'Procent (%)'),
        ('fixed', 'Sta\u0142a kwota (z\u0142)'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    uses_limit = models.IntegerField(null=True, blank=True, help_text="Maksymalna liczba u\u017c\u0119ć (puste = bez limitu)")
    times_used = models.IntegerField(default=0)
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Minimalna warto\u015b\u0107 zam\u00f3wienia")
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} ({self.get_discount_type_display()}: {self.discount_value})"
    
    def save(self, *args, **kwargs):
        """Konwertuj kod na UPPERCASE"""
        self.code = self.code.upper()
        super().save(*args, **kwargs)
    
    def is_valid(self):
        """Sprawdzi czy kod jest jeszcze wa\u017cny"""
        if not self.is_active:
            return False
        if timezone.now() < self.valid_from:
            return False
        if self.valid_until and timezone.now() > self.valid_until:
            return False
        if self.uses_limit and self.times_used >= self.uses_limit:
            return False
        return True
    
    def calculate_discount(self, cart_total):
        """Oblicza ilo\u015b\u0107 rabatu na podstawie typu"""
        if not self.is_valid():
            return Decimal('0.00')
        
        if self.discount_type == 'percent':
            discount = (cart_total * self.discount_value) / Decimal('100')
        else:  # fixed
            discount = self.discount_value
        
        # Rabat nie mo\u017ce by\u0107 wi\u0119kszy ni\u017c ca\u0142a cena
        return min(discount, cart_total)


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Oczekiwanie na p\u0142atno\u015b\u0107'),
        ('paid', 'Op\u0142acone'),
        ('cancelled', 'Anulowane'),
    ]
    
    order_number = models.CharField(max_length=20, unique=True)
    products = models.JSONField(default=dict, help_text="Produkty w zam\u00f3wieniu w JSON")
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_code = models.ForeignKey(
        DiscountCode, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='orders'
    )
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # BLIK
    blik_code = models.CharField(max_length=6, blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.order_number} - {self.get_status_display()}"
    
    def generate_order_number(self):
        """Generuj unikalny numer zam\u00f3wienia"""
        import uuid
        self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"