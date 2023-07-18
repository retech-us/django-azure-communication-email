import django
from django.conf import settings
from django.core.management import call_command


settings.configure(
    INSTALLED_APPS=[
        'django_ace',
    ],
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        },
    },
    MIDDLEWARE_CLASSES=(
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
    ),
    ROOT_URLCONF='',
    SECRET_KEY='not-secret',
)

django.setup()

call_command('test', 'tests', verbosity=3)
