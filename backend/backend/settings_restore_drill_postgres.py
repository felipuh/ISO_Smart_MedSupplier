import os

from .settings import *  # noqa: F401,F403

RESTORE_DB_NAME = os.getenv('RESTORE_DB_NAME')
if not RESTORE_DB_NAME:
    raise RuntimeError('RESTORE_DB_NAME must point to the PostgreSQL restore drill database.')

default_db = DATABASES['default'].copy()  # noqa: F405
if 'postgresql' not in default_db.get('ENGINE', ''):
    raise RuntimeError('Restore drill settings require PostgreSQL.')

default_db['NAME'] = RESTORE_DB_NAME
DATABASES = {
    **DATABASES,  # noqa: F405
    'default': default_db,
}
