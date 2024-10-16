
from pathlib import Path
import os, inspect
from django.contrib.messages import constants as message_constants
import datetime

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

#define padrão de alertas bootstraps das mensagens no sistema
MESSAGE_TAGS = {message_constants.DEBUG: 'debug',
                message_constants.INFO: 'info',
                message_constants.SUCCESS: 'success',
                message_constants.WARNING: 'warning',
                message_constants.ERROR: 'danger',}

#static files for docker
#media /data/web/media
#static /data/web/static
DATA_DIR = BASE_DIR.parent / 'data' / 'web'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'change-me')

# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = bool(int(os.getenv('DEBUG', 0)))
DEBUG = True

ALLOWED_HOSTS = [
    h.strip() for h in os.getenv('ALLOWED_HOSTS', '').split(',')
    if h.strip()
]

CSRF_TRUSTED_ORIGINS = [
    'http://numerodasorte.idbatacadistas.com.br',
    'http://localhost:1337',  # ajuste conforme seu uso local
    'http://172.16.20.150:1337',
    'http://192.168.253.111:1337',
    'http://187.87.33.18:1337',
    'http://172.16.20.106:1337',
    'http://172.16.23.23:1337',
    'http://10.10.1.6:1337',
    'http://10.10.1.3:1337',
    'http://127.0.0.1:1337',
    'http://187.62.77.174:1337',
    'http://190.5.208.50:1337'
]



# Application definition

INSTALLED_APPS = [
    'baton',
    'admin_tools_stats',  # this must be BEFORE 'admin_tools' and 'django.contrib.admin'
    'django_nvd3',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cpfcli',
    'acounts',
    'reusable',
    'relatorios',
    'baton.autodiscover',
    'django_cleanup.apps.CleanupConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django.middleware.common.CommonMiddleware",
    'project.middlewares.CustomCSSMiddleware',
    'project.middlewares.AccessLogMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR , "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'reusable.context_processors.css_vars_processor',
            ],
        },
    },
]


WSGI_APPLICATION = 'project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'change-me'),
        'NAME': os.getenv('POSTGRES_DB', 'change-me'),
        'USER': os.getenv('POSTGRES_USER', 'change-me'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'change-me'),
        'HOST': os.getenv('POSTGRES_HOST', 'change-me'),
        'PORT': os.getenv('POSTGRES_PORT', 'change-me'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'utils.paginator.YourPagination',
    'PAGE_SIZE': 10,
}

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Rio_Branco'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/


STATIC_URL = '/static/'
STATIC_ROOT = DATA_DIR / 'staticfiles'
if DEBUG:
    STATICFILES_DIRS = (
    DATA_DIR / 'static',
)

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

MEDIA_URL = '/media/'
MEDIA_ROOT = DATA_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = 'login'

LOGOUT_REDIRECT_URL = '/'
LOGOUT_URL = 'logout'

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
}


BATON = {
    'SITE_HEADER': 'Painel administrativo',
    'SITE_TITLE': 'SysP',
    'INDEX_TITLE': 'Painel administrativo',
    'SUPPORT_HREF': 'https://github.com/otto-torino/django-baton/issues',
    'COPYRIGHT': 'Copyright © 2024 <a href="/">SysPremia</a>', # noqa
    'POWERED_BY': '<a href="/">InnovaPlus</a>',
    'CONFIRM_UNSAVED_CHANGES': True,
    'SHOW_MULTIPART_UPLOADING': True,
    'ENABLE_IMAGES_PREVIEW': True,
    'CHANGELIST_FILTERS_IN_MODAL': True,
    'CHANGELIST_FILTERS_ALWAYS_OPEN': True,
    'CHANGELIST_FILTERS_FORM': True,
    'CHANGEFORM_FIXED_SUBMIT_ROW': True,
    'MENU_ALWAYS_COLLAPSED': False,
    'MENU_TITLE': 'Menu',
    'MESSAGES_TOASTS': False,
    'GRAVATAR_DEFAULT_IMG': 'retro',
    'GRAVATAR_ENABLED': True,
    'LOGIN_SPLASH': '/static/core/img/login-splash.png',
    'FORCE_THEME': None,
    'BATON_CLIENT_ID': '1545454554sdsdsdsds',
    'BATON_CLIENT_SECRET': 'e45e4w541s41ds545e4w',
}


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'change-me')
EMAIL_PORT = os.getenv('EMAIL_PORT', 'change-me')
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'change-me')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'change-me')
PASSWORD_RESET_TIMEOUT_DAYS = 1
EMAIL_TEMPLATE_NAME = 'password_reset_email_custom.html'
#DEFAULT_FROM_EMAIL  = os.getenv('DEFAULT_FROM_EMAIL', 'change-me')
