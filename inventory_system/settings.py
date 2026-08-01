"""
Django settings for inventory_system project.
"""
import os
from pathlib import Path

import dj_database_url
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1']),
)

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY', default='django-insecure-dev-key-change-in-production')
DEBUG = env('DEBUG')

# Render يضبط هذه المتغيرات تلقائياً
IS_RENDER = bool(os.environ.get('RENDER'))
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')
RENDER_EXTERNAL_URL = os.environ.get('RENDER_EXTERNAL_URL', '').rstrip('/')

# ─── ALLOWED_HOSTS ───────────────────────────────────────────
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

if RENDER_EXTERNAL_HOSTNAME and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

if DEBUG:
    ALLOWED_HOSTS = ['*']
elif IS_RENDER:
    if '.onrender.com' not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append('.onrender.com')

# ─── CSRF (مطلوب لـ HTTPS على Render) ───────────────────────
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])

if RENDER_EXTERNAL_URL and RENDER_EXTERNAL_URL not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append(RENDER_EXTERNAL_URL)

if RENDER_EXTERNAL_HOSTNAME:
    origin = f'https://{RENDER_EXTERNAL_HOSTNAME}'
    if origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(origin)

if IS_RENDER:
    if 'https://*.onrender.com' not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append('https://*.onrender.com')

# بيئات التطوير السحابية (Cursor Cloud Agent, ngrok, ...)
if DEBUG or not IS_RENDER:
    for pattern in (
        'https://*.agent.cvm.dev',
        'https://*.cvm.dev',
        'http://localhost',
        'http://127.0.0.1',
    ):
        if pattern not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(pattern)

# إزالة التكرار
CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(CSRF_TRUSTED_ORIGINS))

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'inventory',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'inventory.middleware.CloudDevMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'inventory_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'inventory.context_processors.low_stock_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'inventory_system.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Render PostgreSQL يتطلب SSL
if IS_RENDER and 'postgresql' in DATABASES['default'].get('ENGINE', ''):
    DATABASES['default'].setdefault('OPTIONS', {})
    DATABASES['default']['OPTIONS']['sslmode'] = 'require'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Asia/Riyadh'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# قيم افتراضية لإعدادات الكوكيز (يُعدّلها CloudDevMiddleware عند الحاجة)
USE_X_FORWARDED_HOST = False
CSRF_USE_SESSIONS = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'
SECURE_PROXY_SSL_HEADER = None

# إعدادات HTTPS — فقط على Render (ليس محلياً حتى لو DEBUG=False)
if IS_RENDER:
    USE_X_FORWARDED_HOST = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SAMESITE = 'Lax'

CSRF_FAILURE_VIEW = 'inventory.views.csrf_failure'
