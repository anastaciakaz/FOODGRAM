import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(os.path.join(BASE_DIR.parent.parent.parent,
                         'foodgram-project-react/infra/.env'),
            verbose=True)

DEBUG = os.getenv('DEBUG_VAR_F')

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE',
                            default='django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME', default='postgres'),
        'USER': os.getenv('POSTGRES_USER', default='postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', default='postgres'),
        'HOST': os.getenv('DB_HOST', default='db'),
        'PORT': os.getenv('DB_PORT', default='5432')
    }
}
