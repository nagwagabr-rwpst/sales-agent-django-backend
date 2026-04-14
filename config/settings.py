"""
Django settings for config project.
"""

import environ
from pathlib import Path

# ==============================
# BASE DIR
# ==============================
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================
# ENVIRONMENT VARIABLES
# ==============================
env = environ.Env(
    DEBUG=(bool, False)
)

# اقرأ ملف .env من root المشروع
environ.Env.read_env(BASE_DIR / ".env")

# ==============================
# CORE SETTINGS
# ==============================
SECRET_KEY = env("SECRET_KEY")

DEBUG = env("DEBUG")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# ==============================
# APPLICATIONS
# ==============================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',

    # MyApp
    'core',
    'accounts',
    'odoo',
]

# ==============================
# MIDDLEWARE
# ==============================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ==============================
# URL CONFIG
# ==============================
ROOT_URLCONF = 'config.urls'

# ==============================
# TEMPLATES
# ==============================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ==============================
# WSGI / ASGI
# ==============================
WSGI_APPLICATION = 'config.wsgi.application'

# ==============================
# DATABASE (PostgreSQL via Docker)
# ==============================
DATABASES = {
    "default": env.db()
}

# ==============================
# PASSWORD VALIDATION
# ==============================
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

# ==============================
# INTERNATIONALIZATION
# ==============================
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# ==============================
# STATIC FILES
# ==============================
STATIC_URL = 'static/'

# ==============================
# DEFAULT PRIMARY KEY
# ==============================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================
# DRF CONFIG (مهم جدًا للموبايل)
# ==============================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# ==============================
# JWT (SimpleJWT)
# ==============================
SIMPLE_JWT = {
    # Keep defaults for Phase 1.
}