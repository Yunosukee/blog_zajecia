# 🛍️ Sklep E-Commerce Django

Pełnofunkcyjny sklep internetowy zbudowany z Django z koszykiem, kodami rabatowymi i płatnością BLIK.

## ✨ Funkcjonalności

✅ **Katalog produktów**
- Wyświetlanie produktów
- Kategorie produktów
- Szczegółowy opis i ceny
- Zarządzanie stanem magazynowym

✅ **Koszyk (Session-based)**
- Dodawanie/usuwanie produktów
- Edycja ilości
- Czyszczenie koszyka

✅ **Kody rabatowe**
- Rabaty procentowe (np. 10%)
- Rabaty stałe (np. -50 zł)
- Limit użycia kodów
- Data ważności
- Minimalna wartość zamówienia

✅ **Płatności**
- Kod BLIK (6 cyfr)
- Automatyczne zmniejszenie stanu magazynowego
- Śledzenie zamówień
- Historia transakcji

✅ **Admin Panel**
- Zarządzanie produktami
- Edycja cen i stanu magazynowego
- Zarządzanie kodami rabatowymi
- Przeglądanie zamówień

✅ **Responsywny UI**
- Bootstrap 5
- Mobile-friendly
- Nowoczesny design

## 🚀 Szybki Start

### Wymagania
- Python 3.9+
- pip

### Instalacja

```bash
# Sklonuj repo
git clone https://github.com/TWOJ_LOGIN/sklep.git
cd sklep/blog_zajecia

# Utwórz venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Zainstaluj zależności
pip install -r requirements.txt

# Migracje
python manage.py migrate

# Stwórz admina
python manage.py createsuperuser

# Uruchom serwer
python manage.py runserver
```

Sklep dostępny na: **http://localhost:8000**
Admin: **http://localhost:8000/admin**

## 📁 Struktura Projektu

```
blog_zajecia/
├── blog/                    # App z logiką sklepu
│   ├── models.py           # Modele (Product, Order, DiscountCode)
│   ├── views.py            # Views (koszyk, płatności)
│   ├── forms.py            # Formularze (BLIK, rabaty)
│   ├── urls.py             # Routing
│   └── admin.py            # Admin panel
├── core/                   # Konfiguracja Django
├── templates/              # HTML templates
│   ├── base.html
│   ├── product_list.html
│   ├── cart.html
│   ├── checkout.html
│   └── payment_success.html
├── static/                 # CSS/JS
├── media/                  # Zdjęcia produktów
└── db.sqlite3             # Baza danych
```

## 🛠️ API Endpoints

### Produkty
- GET `/` - Lista produktów
- GET `/product/<id>/` - Szczegóły produktu
- GET `/product/new/` - Dodaj produkt (admin)
- POST `/product/new/` - Zapisz produkt (admin)

### Koszyk
- GET `/cart/` - Widok koszyka
- POST `/cart/add/<id>/` - Dodaj do koszyka
- POST `/cart/remove/<id>/` - Usuń z koszyka
- POST `/cart/update/<id>/` - Zmień ilość
- POST `/cart/clear/` - Wyczyść koszyk

### Rabaty
- POST `/cart/apply-discount/` - Aplikuj kod rabatowy
- POST `/cart/remove-discount/` - Usuń kod

### Płatności
- GET `/checkout/` - Strona finalizacji
- POST `/checkout/process-payment/` - Przetwórz BLIK
- GET `/payment/success/<id>/` - Potwierdzenie

## 📊 Modele Danych

### Product
```python
- name: CharField (255)
- description: TextField
- image: ImageField
- price: DecimalField
- stock: IntegerField
- category: ForeignKey(Category)
```

### Order
```python
- order_number: CharField (unique)
- products: JSONField
- total_price: DecimalField
- discount_amount: DecimalField
- final_price: DecimalField
- blik_code: CharField (6)
- status: 'pending' | 'paid' | 'cancelled'
```

### DiscountCode
```python
- code: CharField (unique)
- discount_type: 'percent' | 'fixed'
- discount_value: DecimalField
- is_active: Boolean
- valid_from/until: DateTimeField
```

## 🚀 Deployment

Instrukcje do wdrożenia na PythonAnywhere znajdują się w: `DEPLOYMENT.md`

TL;DR:
```bash
git push do GitHub → PythonAnywhere pull → Reload
```

## 🔐 Bezpieczeństwo

- CSRF protection (Django middleware)
- Session-based cart (bezpieczny)
- Admin login required (edit produktów)
- Input validation (BLIK, kody)
- SQL injection protection (ORM)

## 📝 Licencja

MIT

## 👨‍💻 Author

Sklep stworzony z ❤️ dla nauki Django

---

**Status**: ✅ Production Ready

**Wersja**: 1.0.0

**Ostatnia aktualizacja**: Marzec 2026
