from split_settings.tools import include
from decouple import config

include('base.py')

if 'dev' == config('DJANGO_ENV'):
    include('development.py')
if 'prod' == config('DJANGO_ENV'):
    include('production.py')
