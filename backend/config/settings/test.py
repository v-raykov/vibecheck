from . import base

DATABASES = base.DATABASES.copy()

DATABASES['default'].update({
    'USER': 'root',
    'PASSWORD': 'root',
})

INSTALLED_APPS = base.INSTALLED_APPS + [
    'django_extensions',
]