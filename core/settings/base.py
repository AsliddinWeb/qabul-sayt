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
    "site_title": "XIU Admin Panel",
    "site_header": "Xalqaro Innovatsion Universitet",
    "site_brand": "XIU Admin",
    "welcome_sign": "Xalqaro Innovatsion Universitet Admin Panelga Xush Kelibsiz",

    "site_logo": "/assets/images/new/logo-one.png",
    "login_logo": "/assets/images/new/logo-one.png",
    "login_logo_dark": "/assets/images/new/logo-one.png",
    "site_logo_classes": "img-circle",
    "site_icon": "/assets/images/new/logo-one.png",
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
    # Sidebar ordering va grouping
    "order_with_respect_to": [
        # 1. Asosiy arizalar moduli
        "applications",
        "applications.application",
        
        # 2. Foydalanuvchilar va profillar
        "users", 
        "users.user",
        "users.abituriyentprofile",
        "users.operatorprofile",
        "users.marketingprofile",
        "users.miniadminprofile", 
        "users.adminprofile",
        "users.phoneverification",
        
        # 3. Diplomlar va transfer
        "diploms",
        "diploms.diplom",
        "diploms.transferdiplom",
        "diploms.course",
        "diploms.educationtype",
        "diploms.institutiontype",
        
        # 4. Dasturlar va filiallar
        "programs",
        "programs.branch",
        "programs.educationlevel", 
        "programs.educationform",
        "programs.program",
        
        # 5. Hududlar
        "regions",
        "regions.country",
        "regions.region", 
        "regions.district",
        
        # 6. Django asosiy modellar
        "auth",
        "auth.user",
        "auth.group",
        "admin",
        "contenttypes",
        "sessions",
    ],
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

    # Custom navigation grouping
    "custom_links": {
        "applications": [
            {
                "name": "✅ Qabul Qilinganlar", 
                "url": "/admin/applications/application/?status=qabul_qilindi",
                "icon": "fas fa-check-circle",
                "permissions": ["applications.view_application"]
            },
            {
                "name": "⏳ Kutilayotganlar",
                "url": "/admin/applications/application/?status=topshirildi",
                "icon": "fas fa-hourglass-half",
                "permissions": ["applications.view_application"]
            }
        ],
        "users": [
            {
                "name": "🎓 Abituriyentlar",
                "url": "/admin/users/abituriyentprofile/",
                "icon": "fas fa-user-graduate",
                "permissions": ["users.view_abituriyentprofile"]
            },
            {
                "name": "📱 SMS Kodlar",
                "url": "/admin/users/phoneverification/",
                "icon": "fas fa-mobile-alt",
                "permissions": ["users.view_phoneverification"]
            }
        ],
        "diploms": [
            {
                "name": "📜 O'rta Maktab Diplomlari",
                "url": "/admin/diploms/diplom/",
                "icon": "fas fa-scroll",
                "permissions": ["diploms.view_diplom"]
            },
            {
                "name": "🔄 Transfer Diplomlari", 
                "url": "/admin/diploms/transferdiplom/",
                "icon": "fas fa-exchange-alt",
                "permissions": ["diploms.view_transferdiplom"]
            }
        ]
    },

    # App va model nomlarini o'zgartirish
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "applications.application": "collapsible",
        "users.abituriyentprofile": "horizontal_tabs",
    },
    
    # UI sozlamalar
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "related_modal_active": False,
    
    # Ranglar va tema
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary", 
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    },
    
    # Language va localization
    "language_chooser": False,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    
    # Default iconlar
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    
    # Search va UI
    "search_model": "applications.application",
    "user_avatar": None,
    
    # Top menu
    "topmenu_links": [
        {"name": "🏠 Bosh Sahifa", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "📊 Barcha arizalar", "url": "/admin/applications/application/", "permissions": ["applications.view_application"]},
    ],
    
    # Copyright
    "copyright": "Xalqaro Innovatsion Universitet © 2025",
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