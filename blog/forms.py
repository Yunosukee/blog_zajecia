from django import forms
from .models import Product, Category, DiscountCode

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'image', 'price', 'stock', 'category']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dodaj Bootstrap klasy do wszystkich pół
        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Np. iPhone 15 Pro',
        })
        self.fields['description'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Opisz cechy i specyfikacje produktu...',
            'rows': '5',
        })
        self.fields['price'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '0.00',
            'step': '0.01',
        })
        self.fields['stock'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '0',
            'type': 'number',
        })
        self.fields['category'].widget.attrs.update({
            'class': 'form-control',
        })
        self.fields['image'].widget.attrs.update({
            'class': 'form-control',
            'accept': 'image/*',
        })


class QuickEditForm(forms.ModelForm):
    """Forma do szybkiej edycji ceny i stanu magazynowego"""
    class Meta:
        model = Product
        fields = ['price', 'stock']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['price'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0',
        })
        self.fields['stock'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '0',
            'type': 'number',
            'min': '0',
        })


class DiscountCodeForm(forms.Form):
    """Formularz do zastosowania kodu rabatowego"""
    code = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Wpisz kod rabatowy...',
        })
    )


class BlikPaymentForm(forms.Form):
    """Formularz do płatności BLIK"""
    blik_code = forms.CharField(
        max_length=6,
        min_length=6,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg text-center',
            'placeholder': '000000',
            'inputmode': 'numeric',
            'pattern': '[0-9]{6}',
            'maxlength': '6',
        }),
        help_text='Wpisz 6-cyfrowy kod BLIK'
    )
    
    def clean_blik_code(self):
        """Walidacja - tylko cyfry"""
        code = self.cleaned_data['blik_code']
        if not code.isdigit():
            raise forms.ValidationError('Kod BLIK musi zawierać tylko cyfry!')
        if len(code) != 6:
            raise forms.ValidationError('Kod BLIK musi mieć 6 cyfr!')
        return code