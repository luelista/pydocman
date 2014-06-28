"""
Django settings for teamwiki project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.conf import global_settings

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '+9box+7qiq9#prj&k4+z$q(o8*^h2h1(z1n$q6ow1ev=!i1#a8'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

THEWIKI_DATA_DIR = os.path.join(BASE_DIR, 'data/twdata')
THEWIKI_PAGE_DIR = THEWIKI_DATA_DIR + '/pagedata'

# Customize Auth
AUTH_USER_MODEL = 'thewiki.User'

# override in local_settings.py
PASSWORD_SALT = 'dev-salt'

TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]
ROOT_HOSTCONF = 'teamwiki.hosts'
DEFAULT_HOST = 'default'

# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_hosts',
    'thewiki',
    'dropmefiles',
    'django.contrib.admin', 
    'rest_framework'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_hosts.middleware.HostsMiddleware',
    'dropmefiles.login.LoginCheckMiddleware'
)

ROOT_URLCONF = 'teamwiki.admin_urls'

APPEND_SLASH = True

WSGI_APPLICATION = 'teamwiki.wsgi.application'

TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
      'dropmefiles.login.session_info_context',
      "django.core.context_processors.request",
      )

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAdminUser',),
    'PAGINATE_BY': 10
}
# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'data/db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root/')

DROPME_STORE_DIRECTORY = os.path.join(BASE_DIR, 'data/store')



class InvalidString(str):
    strs = ""
    def __str__(self):
        return "Undefined variable or unknown value for: %s" % self.strs
    def __mod__(self, other):
        self.strs = other
        #from django.template.base import TemplateSyntaxError
        #raise TemplateSyntaxError(
        #    "Undefined variable or unknown value for: %s" % other)

TEMPLATE_STRING_IF_INVALID = InvalidString("%s")



try:
    from local_settings import *
except ImportError:
    pass


