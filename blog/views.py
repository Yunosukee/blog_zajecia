from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponseForbidden, JsonResponse
from django.utils import timezone
from .forms import ProductForm, QuickEditForm, DiscountCodeForm, BlikPaymentForm
from .models import Product, Category, DiscountCode, Order

# Widok listy wszystkich produktów
def product_list(request):
    products = Product.objects.all()
    category_filter = request.GET.get('category')
    if category_filter:
        products = products.filter(category_id=category_filter)
    
    categories = Category.objects.all()
    return render(request, 'product_list.html', {
        'products': products,
        'categories': categories,
        'selected_category': category_filter
    })

# Widok szczegółów produktu
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})

# Widok tworzenia produktu - TYLKO ADMIN
@login_required(login_url='admin:login')
def create_product(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Nie masz uprawnień do dodawania produktów!")
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form, 'action': 'Dodaj'})

# Widok edycji produktu - TYLKO ADMIN
@login_required(login_url='admin:login')
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if not request.user.is_staff:
        return HttpResponseForbidden("Nie masz uprawnień do edycji produktów!")
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'product_form.html', {'form': form, 'action': 'Edytuj'})

# Widok usuwania produktu - TYLKO ADMIN
@login_required(login_url='admin:login')
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if not request.user.is_staff:
        return HttpResponseForbidden("Nie masz uprawnień do usuwania produktów!")
    
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'product_delete.html', {'product': product})

# Widok wylogowania
def user_logout(request):
    logout(request)
    return redirect('product_list')

# ========== CART VIEWS ==========

def get_cart(request):
    """Pobierz koszyk z sesji"""
    if 'cart' not in request.session:
        request.session['cart'] = {}
    return request.session['cart']

def add_to_cart(request, pk):
    """Dodaj produkt do koszyka"""
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        cart = get_cart(request)
        
        # Sprawdzenie czy jest wystarczająco towaru
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > product.stock:
            return redirect('product_detail', pk=pk)
        
        product_id = str(pk)
        if product_id in cart:
            cart[product_id]['quantity'] += quantity
        else:
            cart[product_id] = {
                'quantity': quantity,
                'price': str(product.price),
                'name': product.name,
                'image_url': product.image.url if product.image else ''
            }
        
        request.session.modified = True
        return redirect('cart_view')
    
    return redirect('product_detail', pk=pk)

def cart_view(request):
    """Widok koszyka"""
    cart = get_cart(request)
    cart_items = []
    total_price = 0
    discount_amount = 0
    final_price = 0
    applied_discount = None
    error_message = None
    success_message = None
    
    # Pobierz komunikaty z sesji
    if 'discount_error' in request.session:
        error_message = request.session.pop('discount_error')
        request.session.modified = True
    
    if 'discount_success' in request.session:
        success_message = request.session.pop('discount_success')
        request.session.modified = True
    
    for product_id, item in cart.items():
        try:
            product = Product.objects.get(pk=product_id)
            item_total = product.price * item['quantity']
            total_price += item_total
            
            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'item_total': item_total,
                'product_id': product_id
            })
        except Product.DoesNotExist:
            # Usuń nieistniejący produkt z koszyka
            del cart[product_id]
            request.session.modified = True
    
    # Sprawdź czy jest stosowany kod rabatowy
    discount_code = request.session.get('discount_code')
    if discount_code:
        try:
            applied_discount = DiscountCode.objects.get(code=discount_code)
            if applied_discount.is_valid():
                discount_amount = applied_discount.calculate_discount(total_price)
            else:
                # Kod stał się nieważny, usuń go
                del request.session['discount_code']
                request.session.modified = True
                applied_discount = None
        except DiscountCode.DoesNotExist:
            if 'discount_code' in request.session:
                del request.session['discount_code']
                request.session.modified = True
    
    final_price = total_price - discount_amount
    
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'discount_amount': discount_amount,
        'final_price': final_price,
        'applied_discount': applied_discount,
        'cart_count': sum(item['quantity'] for item in cart.values()) if cart else 0,
        'error_message': error_message,
        'success_message': success_message,
    })

def remove_from_cart(request, pk):
    """Usuń produkt z koszyka"""
    cart = get_cart(request)
    product_id = str(pk)
    
    if product_id in cart:
        del cart[product_id]
        request.session.modified = True
    
    return redirect('cart_view')

def update_cart(request, pk):
    """Zaktualizuj ilość produktu w koszyku"""
    if request.method == 'POST':
        cart = get_cart(request)
        product_id = str(pk)
        quantity = int(request.POST.get('quantity', 1))
        
        if product_id in cart:
            if quantity <= 0:
                del cart[product_id]
            else:
                product = get_object_or_404(Product, pk=product_id)
                if quantity > product.stock:
                    quantity = product.stock
                cart[product_id]['quantity'] = quantity
            
            request.session.modified = True
    
    return redirect('cart_view')

def clear_cart(request):
    """Wyczyść koszyk"""
    if 'cart' in request.session:
        del request.session['cart']
        request.session.modified = True
    
    return redirect('product_list')

# ========== QUICK EDIT VIEWS ==========

@login_required(login_url='admin:login')
def quick_edit_product(request, pk):
    """Szybka edycja ceny i stanu magazynowego"""
    product = get_object_or_404(Product, pk=pk)
    if not request.user.is_staff:
        return HttpResponseForbidden("Nie masz uprawnień do edycji produktów!")
    
    if request.method == 'POST':
        form = QuickEditForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_detail', pk=product.pk)
    else:
        form = QuickEditForm(instance=product)
    
    return render(request, 'quick_edit_product.html', {
        'form': form,
        'product': product
    })

# ========== DISCOUNT CODE VIEWS ==========

def apply_discount(request):
    """Zastosuj kod rabatowy do koszyka"""
    if request.method == 'POST':
        form = DiscountCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code'].upper().strip()
            
            try:
                # Case-insensitive szukanie
                discount = DiscountCode.objects.get(code__iexact=code)
                
                if not discount.is_valid():
                    request.session['discount_error'] = 'Kod rabatowy jest już nieważny lub wygasł!'
                    return redirect('cart_view')
                
                # Pobierz koszyk
                cart = get_cart(request)
                if not cart:
                    request.session['discount_error'] = 'Koszyk jest pusty!'
                    return redirect('cart_view')
                
                # Oblicz sumę koszyka
                cart_total = sum(
                    Product.objects.get(pk=pid).price * item['quantity']
                    for pid, item in cart.items()
                )
                
                # Sprawdź minimalną wartość zamówienia
                if cart_total < discount.min_order_value:
                    request.session['discount_error'] = f'Minimalna wartość zamówienia to {discount.min_order_value} zł'
                    return redirect('cart_view')
                
                # Zapisz kod do sesji (zawsze UPPERCASE)
                request.session['discount_code'] = discount.code.upper()
                request.session.modified = True
                
                # Zaktualizuj times_used
                discount.times_used += 1
                discount.save()
                
                request.session['discount_success'] = f'Kod "{discount.code}" zastosowany pomyślnie!'
                
            except DiscountCode.DoesNotExist:
                request.session['discount_error'] = 'Kod rabatowy nie istnieje!'
                return redirect('cart_view')
    
    return redirect('cart_view')

def remove_discount(request):
    """Usuń kod rabatowy z koszyka"""
    if 'discount_code' in request.session:
        discount_code = request.session['discount_code']
        try:
            discount = DiscountCode.objects.get(code=discount_code)
            discount.times_used -= 1
            discount.save()
        except DiscountCode.DoesNotExist:
            pass
        
        del request.session['discount_code']
        request.session.modified = True
    
    return redirect('cart_view')

# ========== PAYMENT VIEWS ==========

def checkout(request):
    """Przygotowanie do płatności"""
    cart = get_cart(request)
    
    if not cart:
        return redirect('product_list')
    
    # Pobierz dane koszyka
    cart_items = []
    total_price = 0
    
    for product_id, item in cart.items():
        try:
            product = Product.objects.get(pk=product_id)
            item_total = product.price * item['quantity']
            total_price += item_total
            
            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'item_total': item_total,
                'product_id': product_id
            })
        except Product.DoesNotExist:
            pass
    
    # Sprawdź rabat
    discount_amount = 0
    applied_discount = None
    discount_code = request.session.get('discount_code')
    
    if discount_code:
        try:
            applied_discount = DiscountCode.objects.get(code=discount_code)
            if applied_discount.is_valid():
                discount_amount = applied_discount.calculate_discount(total_price)
            else:
                del request.session['discount_code']
                request.session.modified = True
                applied_discount = None
        except DiscountCode.DoesNotExist:
            pass
    
    final_price = total_price - discount_amount
    
    # Formularz BLIK
    form = BlikPaymentForm()
    
    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'discount_amount': discount_amount,
        'final_price': final_price,
        'applied_discount': applied_discount,
        'form': form
    })


def process_payment(request):
    """Przetwórz płatność BLIK"""
    if request.method != 'POST':
        return redirect('checkout')
    
    cart = get_cart(request)
    if not cart:
        return redirect('product_list')
    
    form = BlikPaymentForm(request.POST)
    
    if not form.is_valid():
        return redirect('checkout')
    
    blik_code = form.cleaned_data['blik_code']
    
    # Oblicz ceny
    cart_items = []
    total_price = 0
    
    for product_id, item in cart.items():
        try:
            product = Product.objects.get(pk=product_id)
            item_total = product.price * item['quantity']
            total_price += item_total
            
            cart_items.append({
                'product_id': int(product_id),
                'quantity': item['quantity'],
                'price': str(product.price),
                'name': product.name
            })
        except Product.DoesNotExist:
            pass
    
    # Sprawdź rabat
    discount_amount = 0
    applied_discount = None
    discount_code = request.session.get('discount_code')
    discount_code_obj = None
    
    if discount_code:
        try:
            discount_code_obj = DiscountCode.objects.get(code=discount_code)
            if discount_code_obj.is_valid():
                discount_amount = discount_code_obj.calculate_discount(total_price)
            else:
                discount_code_obj = None
        except DiscountCode.DoesNotExist:
            pass
    
    final_price = total_price - discount_amount
    
    # Stwórz zamówienie
    order = Order()
    order.generate_order_number()
    order.products = {item['product_id']: item for item in cart_items}
    order.total_price = total_price
    order.discount_amount = discount_amount
    order.final_price = final_price
    order.blik_code = blik_code
    order.discount_code = discount_code_obj
    order.status = 'paid'
    order.paid_at = timezone.now()
    order.save()
    
    # Zmniejsz stan magazynowy
    for product_id, item in cart.items():
        try:
            product = Product.objects.get(pk=product_id)
            product.stock -= item['quantity']
            product.save()
        except Product.DoesNotExist:
            pass
    
    # Wyczyść koszyk i sesję
    del request.session['cart']
    if 'discount_code' in request.session:
        del request.session['discount_code']
    request.session.modified = True
    
    # Przekieruj do potwierdzenia
    return redirect('payment_success', order_id=order.id)


def payment_success(request, order_id):
    """Ekran potwierdzenia płatności"""
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return redirect('product_list')
    
    return render(request, 'payment_success.html', {
        'order': order
    })