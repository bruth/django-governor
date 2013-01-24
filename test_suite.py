#! /usr/bin/env python
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'

from django.core import management
management.call_command('test', 'tests')
