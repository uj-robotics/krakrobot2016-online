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
TEMPLATE_DEBUG = DEBUG

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

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    #os.path.join(BASE_DIR, "static"),
    #'./media/','./static/','./Templates/',
    #'/home/sulphux/KrakrobotEliminacje/Testerka/KrakRobotTestServ/media/',
    '/home/sulphux/KrakrobotEliminacje/Testerka/KrakRobotTestServ/static/',
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'b+@p@fts@vg%05wqaoga-2i-bc_^i%82h8q@=6iipkfex=q0#s'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'KrakRobotTestServ.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'KrakRobotTestServ.wsgi.application'


TEMPLATE_DIRS = {
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    './Templates/',
    './Templates/registration',
    './Templates/coding',
    './Templates/uploader',
    '../Templates/',
    '../Templates/registration',
    '../Templates/coding',
    '../Templates/uploader',
    '/home/sulphux/KrakrobotEliminacje/Testerka/KrakRobotTestServ/Templates/',
    '/home/sulphux/KrakrobotEliminacje/Testerka/KrakRobotTestServ/Templates/registration',
    '/home/sulphux/KrakrobotEliminacje/Testerka/KrakRobotTestServ/Templates/coding',
    '/home/sulphux/KrakrobotEliminacje/Testerka/KrakRobotTestServ/Templates/uploader',
}

#ALLOWED_HOSTS = ['localhost']

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'registration',
    'KrakRobotTestServ.uploader',
)

# registration settings

ACCOUNT_ACTIVATION_DAYS = 2
LOGIN_REDIRECT_URL = '/'

# mail server options
# TODO: find sending mails method

EMAIL_HOST = 'smtp.poczta.onet.pl'
EMAIL_HOST_USER = 'joe.doe@vp.pl'
EMAIL_HOST_PASSWORD = '23cichusoWE'
DEFAULT_FROM_EMAIL = 'joe.doe@vp.pl'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
