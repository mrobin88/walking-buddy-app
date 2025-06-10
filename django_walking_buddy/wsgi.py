"""
WSGI config for walking_buddy project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_walking_buddy.settings')

application = get_wsgi_application() 