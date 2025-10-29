"""
Development settings
"""
from .base import *

DEBUG = True

# Django Debug Toolbar
if 'django_debug_toolbar' not in INSTALLED_APPS:
    INSTALLED_APPS += ['django_debug_toolbar']

if 'debug_toolbar.middleware.DebugToolbarMiddleware' not in MIDDLEWARE:
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Security settings (relaxed for development)
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# CORS - allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

