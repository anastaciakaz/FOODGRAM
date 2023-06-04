import os
from pathlib import Path

from dotenv import load_dotenv
from split_settings.tools import include

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(os.path.join(BASE_DIR.parent.parent.parent,
                         'foodgram-project-react/infra/.env'),
            verbose=True)

include('base.py')

if 'dev' == os.getenv('DJANGO_ENV'):
    include('development.py')
if 'prod' == os.getenv('DJANGO_ENV'):
    include('production.py')
