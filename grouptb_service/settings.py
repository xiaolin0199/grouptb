# -*- coding: utf-8 -*-
"""
Django settings for grouptb_service project.

Generated by 'django-admin startproject' using Django 1.8.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

import local_settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CSRF_COOKIE_NAME = 'grouptb-service-csrftoken'


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'g(gj^rlbxdy!2=gw0$_$^mdkf)s+ns=6e&92%dpi0-rvgzq4q+'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = local_settings.DEBUG

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': local_settings.DATABASE_NAME,
        'HOST': local_settings.DATABASE_HOST,
        'PORT': local_settings.DATABASE_PORT,
        'USER': local_settings.DATABASE_USER,
        'PASSWORD': local_settings.DATABASE_PASSWORD,
        'OPTIONS': {
            'charset':'utf8mb4',
        },
    }
}
# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'grouptb_app',
    'grouptb_bs_app',
    'operationlog_app',
    'upyun_app',
    'upyun_bs_app',
)

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/
LANGUAGE_CODE = 'zh-hans'
LANGUAGE_COOKIE_NAME = 'grouptb-service-django_language'

LOGIN_URL = 'admin:login'

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'grouptb_service.utils.middlewares.JsonResponseMiddleware',
    'grouptb_service.utils.middlewares.OperationLogMiddleware',
    'grouptb_service.utils.middlewares.RequireLoginMiddleware',
)

ROOT_URLCONF = 'grouptb_service.urls'

SESSION_COOKIE_NAME = 'grouptb-service-sessionid'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
STATIC_ROOT = local_settings.STATIC_ROOT
STATIC_URL = '/static/grouptb-service/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': DEBUG,
        },
    },
]

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

WSGI_APPLICATION = 'grouptb_service.wsgi.application'
