from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/new/', views.create_product, name='create_product'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/<int:pk>/edit/', views.edit_product, name='edit_product'),
    path('product/<int:pk>/quick-edit/', views.quick_edit_product, name='quick_edit_product'),
    path('product/<int:pk>/delete/', views.delete_product, name='delete_product'),
    path('logout/', views.user_logout, name='logout'),
    
    # Koszyk
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:pk>/', views.update_cart, name='update_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    
    # Kody rabatowe
    path('cart/apply-discount/', views.apply_discount, name='apply_discount'),
    path('cart/remove-discount/', views.remove_discount, name='remove_discount'),
    
    # Płatność
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/process-payment/', views.process_payment, name='process_payment'),
    path('payment/success/<int:order_id>/', views.payment_success, name='payment_success'),
]
