import os

from decouple import config

if config('DEBUG', default=False, cast=bool):
    from .dev import *
else:
    from .production import *
