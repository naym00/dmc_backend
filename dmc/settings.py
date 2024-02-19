from dotenv import load_dotenv
from datetime import timedelta
from pathlib import Path
import os

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_DIR= BASE_DIR / 'media'



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-%a@0fn276$a5mhi3jq+)au@+*#^)f5l5dyzur6ng+%1^y8w@=m'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'employee',
    'rest_framework',
    'django.core.files.storage',
    'department',
    'designation',
    'empgrp',
    'devices',
    'role',
    'empfiles',
    'grpdev',
    'corsheaders',
    'login',
    'rest_framework_simplejwt',
    'log',
    'structuedlog',
    'forget_password',
    'attendance_report',
    'syncInfo',
    'shift_management',
    'device_status',
    'archive_log',
    'employee_csv',
    'shift_assign',
    'dashboard',
    'security',
    'employee_list_add',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'dmc.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'dmc.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # }
    "default": {
        "ENGINE": os.getenv("DATABASE_ENGI"),
        "NAME": os.getenv("DATABASE_NAME"),
        "USER": os.getenv("DATABASE_USER"),
        "PASSWORD": os.getenv("DATABASE_PASS"),
        "HOST": os.getenv("DATABASE_HOST"),
        "PORT": os.getenv("DATABASE_PORT"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


## cUSTOM 
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # 'auth.auth.CustomJWTAuthentication',

    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,  # Set the default page size
}


##austom allowed origins are here
CORS_ALLOWED_ORIGINS = [
    'http://10.10.23.89:3000',
    'http://10.10.23.16:3004',
    'http://10.10.23.68:3000',
    'http://10.10.20.218:3000',
    'http://10.10.20.218:3004',
    'http://10.10.23.89:3004',
    'http://10.10.23.68:3004',
    'http://113.212.109.147:3000',
    'http://10.10.22.220:3004',
    'http://192.168.31.24:3004',
    'http://10.10.23.61:3004',
    'http://192.168.0.105:3004',
    'http://*',
]
 
CORS_ALLOW_HEADERS = ['*']


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
# media root
MEDIA_ROOT = MEDIA_DIR
MEDIA_URL = "/media/"

###
AUTH_USER_MODEL = 'employee.Employee'

# settings.py

AUTHENTICATION_BACKENDS = [
    'login.backends.EmployeeIdBackend',  # Add your custom backend if needed
    'django.contrib.auth.backends.ModelBackend',  # Default ModelBackend
]
###
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    # ... other hashers ...
]
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'USER_ID_FIELD': 'employee_id',
}

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

###email settings

# settings.py

EMAIL_BACKEND = os.getenv("EMAIL_BACKEND")
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
# DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")

TIME_ZONE = 'Asia/Dhaka'
