# settings.py (medicliq_project)

from pathlib import Path
import os
from decouple import config
from django.utils.translation import gettext_lazy as _
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_ROOT = os.path.join(BASE_DIR, 'temp')
MEDIA_URL = '/media/'


# SECRET_KEY & DEBUG should be set as environment variables in production
SECRET_KEY = config('SECRET_KEY', default='your_default_secret_key')
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['*']  # For development. Update for production with actual domains/IPs

RAZORPAY_KEY_ID = "rzp_test_oIP043kHtRWfHZ"
RAZORPAY_KEY_SECRET = "CQfkRQnBbQYjnUnP4KdWE9Ah"

# Razorpay API Keys (use environment variables for production)
RAZORPAY_API_KEY = config('RAZORPAY_API_KEY', default='rzp_test_oIP043kHtRWfHZ')
RAZORPAY_SECRET_KEY = config('RAZORPAY_SECRET_KEY', default='CQfkRQnBbQYjnUnP4KdWE9Ah')


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap4',
    'medicliq_database',  # Include your database app
    'medicliq_payment',   # Include your payment app
]
CRISPY_TEMPLATE_PACK = 'bootstrap4'
# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'medicliq_project.urls'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
           os.path.join(BASE_DIR,'templates')  # Template directory
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'medicliq_project.wsgi.application'

# Database configuration (using SQLite for development)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # SQLite database location
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Localization settings
# LANGUAGE_CODE = 'en'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
USE_L10N = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

LOCALE_PATHS = [
    BASE_DIR / 'locale/',  # Path where translation files will be stored
]

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  # Add your static folder if not already there
]

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # For production


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',  # Your local server
    'http://localhost:8000',  # Localhost
    'https://*.razorpay.com',  # Razorpay API
    'https://api.razorpay.com' # Specific Razorpay API URL
]


LANGUAGES = [
    ('en', _('English')),
    ('hi', _('Hindi')),
    ('mr', _('Marathi')),
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'prescription-upload',
    }
}