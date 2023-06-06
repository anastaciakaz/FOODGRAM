import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(os.path.join(BASE_DIR.parent.parent.parent,
                         'foodgram-project-react/infra/.env'),
            verbose=True)

DEBUG = os.getenv('DEBUG_VAR_F')

ALLOWED_HOSTS = ['158.160.35.159', 'foodgram-projreact.ddns.net']

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE',
                            default='django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME', default='postgres'),
        'USER': os.getenv('POSTGRES_USER', default='postgresus'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', default='postgres'),
        'HOST': os.getenv('DB_HOST', default='localhost'),
        'PORT': os.getenv('DB_PORT', default='5432')
    }
}
