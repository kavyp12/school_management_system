"""
WSGI config for student_management_system project.

It exposes the WSGI callable as a module-level variable named ``application`` and ``app`` for Vercel.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')

application = get_wsgi_application()
app = application  # Required for Vercel