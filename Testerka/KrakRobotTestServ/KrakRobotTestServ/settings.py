"""
Django settings for KrakRobotTestServ project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
#from django.conf.global_settings import TEMPLATE_DIRS, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, STATIC_URL

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = True
TEMPLATE_DEBUG = True

ADMINS = {
    # ('Your Name', 'your_email@example.com'),
}

MANAGERS = ADMINS

# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}


# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

SITE_ID = 1

USE_I18N = True

USE_L10N = True

USE_TZ = True


MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    #os.path.join(BASE_DIR, "static"),
    #'./media/','./static/','./Templates/',
    #'/home/sulphux/KrakrobotEliminacje/Testerka/KrakRobotTestServ/media/',
    #'/home/sulphux/KrakrobotEliminacje/Testerka/KrakRobotTestServ/static/',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'b+@p@fts@vg%05wqaoga-2i-bc_^i%82h8q@=6iipkfex=q0#s'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'KrakRobotTestServ.urls'

WSGI_APPLICATION = 'KrakRobotTestServ.wsgi.application'


TEMPLATE_DIRS = {
    './Templates/',
    './Templates/registration',
    './Templates/coding',
    '../Templates/',
    '../Templates/registration',
    '../Templates/coding',
    '/home/sulphux/KrakrobotEliminacje/Testerka/KrakRobotTestServ/Templates/',
    '/home/sulphux/KrakrobotEliminacje/Testerka/KrakRobotTestServ/Templates/registration',
    '/home/sulphux/KrakrobotEliminacje/Testerka/KrakRobotTestServ/Templates/coding',
}

#ALLOWED_HOSTS = ['localhost']



ROOT_URLCONF = 'KrakRobotTestServ.urls'





# registration settings

ACCOUNT_ACTIVATION_DAYS = 2
LOGIN_REDIRECT_URL = '/'

# mail server options
# TODO: find sending mails method

EMAIL_HOST = 'smtp.poczta.onet.pl'
EMAIL_HOST_USER = 'joe.doe@vp.pl'
EMAIL_HOST_PASSWORD = '23cichusoWE'
DEFAULT_FROM_EMAIL = 'joe.doe@vp.pl'


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'registration',
    'KrakRobotTestServ.uploader',
    'uploader',
)
