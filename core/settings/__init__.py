import os
from decouple import config

# Environment asosida settings faylini tanlash
ENVIRONMENT = config('ENVIRONMENT', default='dev')

if ENVIRONMENT == 'production':
    from .production import *
else:
    from .dev import *
