from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'crispy_forms',
    'crispy_bootstrap5',
]

LOCAL_APPS = [
    'apps.users',
    'apps.regions',
    'apps.diploms',
    'apps.programs',
    'apps.applications',
    'apps.dashboards',
    'apps.pages',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Custom middleware'lar (order muhim!)
    'apps.users.middleware.SecurityMiddleware',
    'apps.users.middleware.PhoneVerificationMiddleware',
    'apps.users.middleware.RoleBasedAccessMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'core.wsgi.application'

# Custom User Model
AUTH_USER_MODEL = 'users.User'

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

LANGUAGE_CODE = 'uz-uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Login URL ni o'zgartirish
LOGIN_URL = 'users:phone_auth'
LOGIN_REDIRECT_URL = 'users:home'
LOGOUT_REDIRECT_URL = 'users:phone_auth'

# Messages framework sozlamalari
from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# SMS xizmati sozlamalari (agar kerak bo'lsa)
# SMS_API_KEY = 'your_sms_api_key'
# SMS_API_URL = 'your_sms_provider_url'

# Cache sozlamalari (agar kerak bo'lsa)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Telefon raqam validatsiya sozlamalari
PHONE_VALIDATION = {
    'COUNTRY_CODE': '+998',
    'MIN_LENGTH': 13,
    'MAX_LENGTH': 13,
    'ALLOWED_OPERATORS': ['90', '91', '93', '94', '95', '97', '98', '99'],
}

# SMS kod sozlamalari
SMS_VERIFICATION = {
    'CODE_LENGTH': 4,
    'EXPIRY_MINUTES': 5,
    'MAX_ATTEMPTS': 3,
    'RATE_LIMIT_MINUTES': 1,
    'HOURLY_LIMIT': 5,
}

# Eskiz.uz sozlamalari
ESKIZ_EMAIL = config('ESKIZ_EMAIL')
ESKIZ_PASSWORD = config('ESKIZ_PASSWORD')
ESKIZ_FROM = config('ESKIZ_FROM')
ESKIZ_CALLBACK_URL = config('ESKIZ_CALLBACK_URL')

# Passport api
PASSPORT_API = config('PASSPORT_API')
