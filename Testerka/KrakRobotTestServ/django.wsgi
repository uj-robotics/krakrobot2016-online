import os
import sys
sys.path.append('C:/wsgi_app')
sys.path.append('C:/wsgi_app/KrakRobotTestServ')

os.environ['DJANGO_SETTINGS_MODULE'] = 'KrakRobotTestServ.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()