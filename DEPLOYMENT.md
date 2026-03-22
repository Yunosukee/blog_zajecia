# 🚀 DEPLOYMENT NA PYTHONANYWHERE

## Krok 1: Przygotuj Git

```bash
cd c:\Users\ldomagala1\Desktop\Foryś\blog_zajecia
git init
git add .
git commit -m "Initial commit - shop ready for deployment"
```

## Krok 2: Utwórz konto na PythonAnywhere

1. Wejdź na https://www.pythonanywhere.com/
2. Zarejestruj się darmowy plan (PythonAnywhere FREE)
3. Potwierdź email

## Krok 3: Połącz GitHub/Git (opcjonalnie)

Jeśli chcesz użyć GitHub-a:

```bash
git remote add origin https://github.com/TWOJ_LOGIN/sklep.git
git push -u origin main
```

## Krok 4: Konsola PythonAnywhere

1. Zaloguj się na PythonAnywhere
2. Kliknij **"Bash console"** (zielony przycisk)

W konsoli PythonAnywhere:

### 4a. Klonuj kod

```bash
git clone https://github.com/TWOJ_LOGIN/sklep.git
cd sklep/blog_zajecia
```

Lub jeśli nie masz GitHub-a, upload-uj pliki przez FTP/Web.

### 4b. Utwórz Virtual Environment

```bash
mkvirtualenv --python=/usr/bin/python3.11 sklep
pip install -r requirements.txt
```

### 4c. Konfiguracja Django

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

Jeśli chcesz, stwórz admina:
```bash
python manage.py createsuperuser
```

## Krok 5: WSGI Configuration

1. W PythonAnywhere kliknij **"Web"** (górny pasek)
2. Kliknij **"Add a new web app"**
3. Wybierz **"Manual configuration"** i **Python 3.11**
4. Czekaj na inicjalizację

W sekcji **"Code"** zmień **WSGI configuration file**:

Path: `/home/TWOJ_LOGIN/TWOJ_LOGIN.pythonanywhere.com_wsgi.py`

Zastąp zawartość:

```python
import os
import sys

# Dodaj ścieżkę do projektu
path = '/home/TWOJ_LOGIN/sklep/blog_zajecia'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## Krok 6: Konfiguracja Static Files

W sekcji **"Static files"** w Web App Settings:

**URL**: `/static/`
**Directory**: `/home/TWOJ_LOGIN/sklep/blog_zajecia/staticfiles`

**URL**: `/media/`
**Directory**: `/home/TWOJ_LOGIN/sklep/blog_zajecia/media`

## Krok 7: Reload Web App

Znowu w **"Web"** kliknij zielony przycisk **"Reload TWOJ_LOGIN.pythonanywhere.com"**

## Krok 8: Zaktualizuj ALLOWED_HOSTS

Wróć do kodu i edytuj `core/settings.py`:

```python
ALLOWED_HOSTS = ['TWOJ_LOGIN.pythonanywhere.com']
```

Reload ponownie!

## ✅ Gotowe!

Twój sklep powinien być dostępny na:
**https://TWOJ_LOGIN.pythonanywhere.com/**

Panel admin:
**https://TWOJ_LOGIN.pythonanywhere.com/admin/**

---

## Troubleshooting

### 404 na staticznych plikach CSS/JS?
```bash
python manage.py collectstatic --noinput
```

### "No module named 'django'"?
```bash
workon sklep && pip install -r requirements.txt
```

### Błąd bazy danych?
```bash
python manage.py migrate
```

### Zmiana kodu?
1. Git pull (jeśli używasz GitHub)
2. **Reload Web App** w PythonAnywhere

---

**WAŻNE**: 
- Darmowy plan PythonAnywhere ma ograniczenia (50MB)
- Po 3 miesiącach bez aktywności konto się zamyka
- Rozważ paid plan za ~5 USD/miesiąc dla bardziej stabilnego hostingu
