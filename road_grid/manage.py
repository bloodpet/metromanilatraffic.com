#!/usr/bin/env python
import sys
import os
from django.core.management import execute_manager
import imp
try:
    imp.find_module('settings') # Assumed to be in the same directory.
except ImportError:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n" % __file__)
    sys.exit(1)

import settings
sys.path.insert(0, os.path.abspath(settings.PARENT_DIR))
sys.path.insert(0, os.path.abspath(os.path.join(settings.PARENT_DIR, 'libs')))
sys.path.insert(0, os.path.abspath(os.path.join(settings.PARENT_DIR, 'apps')))

if __name__ == "__main__":
    execute_manager(settings)
