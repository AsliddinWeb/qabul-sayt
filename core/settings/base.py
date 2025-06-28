from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY')

DJANGO_APPS = [
    # Admin UI
    'jazzmin',

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
    'ckeditor',
]

LOCAL_APPS = [
    'apps.users',
    'apps.regions',
    'apps.diploms',
    'apps.programs',
    'apps.applications',
    'apps.dashboards',
    'apps.pages',
    'apps.settings',
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

# Static files sozlamalari
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Barcha static fayllar shu yerga to'planadi

# Development uchun static fayllar yo'llari
STATICFILES_DIRS = [
    BASE_DIR / 'static',  # Sizning assets papkangiz
]


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

# Cache sozlamalari
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

# CKEditor sozlamalari
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
        'extraPlugins': ','.join([
            'uploadimage',
            'div',
            'autolink',
            'autoembed',
            'embedsemantic',
            'autogrow',
            'widget',
            'lineutils',
            'clipboard',
            'dialog',
            'dialogui',
            'elementspath'
        ]),
    },
}

CKEDITOR_UPLOAD_PATH = "uploads/"

# JAZZMIN SETTINGS
JAZZMIN_SETTINGS = {
    "site_title": "Qabul Admin",
    "site_header": "Qabul Admin",
    "site_brand": "Qabul Admin",
    "site_logo": "/assets/images/new/logo-one.png",
    "login_logo": "/assets/images/new/logo-one.png",
    "login_logo_dark": "/assets/images/new/logo-one.png",
    "site_logo_classes": "img-circle",
    "site_icon": "/assets/images/new/logo-one.png",
    "welcome_sign": "Qabul tizimiga xush kelibsiz!",
    "copyright": "Qabul | qabul.xiuedu.uz",
    "search_model": [],
    "user_avatar": None,
    "topmenu_links": [
        {"name": "Bosh sahifa",  "url": "admin:index", "permissions": ["auth.view_user"]},
    ],
    "usermenu_links": [],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": [],
    # settings.py da JAZZMIN_SETTINGS ichida

    "icons": {
        # Authentication & Users
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        
        # Applications app
        "applications": "fas fa-file-alt",
        "applications.application": "fas fa-paper-plane",
        "applications.applicationstatus": "fas fa-chart-line",
        "applications.admissiontype": "fas fa-graduation-cap",
        
        # Programs app
        "programs": "fas fa-school",
        "programs.branch": "fas fa-building",
        "programs.program": "fas fa-book-open",
        "programs.educationlevel": "fas fa-layer-group",
        "programs.educationform": "fas fa-chalkboard-teacher",
        
        # Diploms app
        "diploms": "fas fa-certificate",
        "diploms.diplom": "fas fa-scroll",
        "diploms.transferdiplom": "fas fa-exchange-alt",
        "diploms.course": "fas fa-list-ol",
        "diploms.educationtype": "fas fa-tags",
        "diploms.institutiontype": "fas fa-university",
        
        # Regions app
        "regions": "fas fa-globe-americas",
        "regions.country": "fas fa-flag",
        "regions.region": "fas fa-map-marker-alt",
        "regions.district": "fas fa-map-pin",
        
        # Users app
        "users": "fas fa-user-circle",
        "users.user": "fas fa-user",
        "users.abituriyentprofile": "fas fa-user-graduate",
        "users.operatorprofile": "fas fa-headset",
        "users.marketingprofile": "fas fa-bullhorn",
        "users.miniadminprofile": "fas fa-user-shield",
        "users.adminprofile": "fas fa-user-tie",
        "users.phoneverification": "fas fa-mobile-alt",
        "users.baseprofile": "fas fa-id-card",
        
        # Django Admin default models
        "admin": "fas fa-tachometer-alt",
        "admin.logentry": "fas fa-history",
        
        # Content types
        "contenttypes": "fas fa-th-large",
        "contenttypes.contenttype": "fas fa-cube",
        
        # Sessions
        "sessions": "fas fa-clock",
        "sessions.session": "fas fa-stopwatch",
        
        # Sites framework (agar ishlatilsa)
        "sites": "fas fa-sitemap",
        "sites.site": "fas fa-globe",
        
        # Django REST Framework (agar ishlatilsa)
        "rest_framework": "fas fa-cogs",
        "authtoken": "fas fa-key",
        "authtoken.token": "fas fa-key",
        "authtoken.tokenproxy": "fas fa-unlock-alt",
        
        # Django allauth (agar ishlatilsa)
        "account": "fas fa-user-shield",
        "socialaccount": "fas fa-share-alt",
        
        # Custom apps (agar mavjud bo'lsa)
        "notifications": "fas fa-bell",
        "payments": "fas fa-credit-card",
        "reports": "fas fa-chart-bar",
        "statistics": "fas fa-analytics",
        "documents": "fas fa-folder-open",
        "contracts": "fas fa-file-contract",
        "dashboard": "fas fa-tachometer-alt",
        "core": "fas fa-cube",
        "utils": "fas fa-tools",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": False,
    "custom_css": False,
    "custom_js": False,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {"accounts.user": "collapsible", "auth.group": "vertical_tabs"},
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-info",
    "accent": "accent-info",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-light-info",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "lux",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}