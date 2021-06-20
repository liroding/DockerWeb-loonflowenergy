"""
WSGI config for helloweb project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os

from os.path import join,dirname,abspath

""" add by liro """
PROJECT_DIR = dirname(dirname(abspath(__file__)))
import sys 
sys.path.insert(0,PROJECT_DIR)
""" add by liro """

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.config")


application = get_wsgi_application()
