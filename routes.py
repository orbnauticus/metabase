# -*- coding: utf-8 -*-

# To enable this route file:
#
# 1. copy <web2py-root-dir>/examples/routes.parametric.example.py to routes.py
# 2. restart web2py (or reload routes in web2py admin interface)
#
# YOU CAN COPY THIS FILE TO ANY APPLICATION'S ROOT DIRECTORY WITHOUT CHANGES!

from fileutils import abspath
from languages import read_possible_languages

possible_languages = read_possible_languages(abspath('applications', app))

routers = dict(
    metabase=dict(
        default_controller='default',
        default_function='index',
        default_language = possible_languages['default'][0],
        languages = [lang for lang in possible_languages if lang != 'default'],
    )
)
# Specify log level for rewrite's debug logging
# Possible values: debug, info, warning, error, critical (loglevels),
#                  off, print (print uses print statement rather than logging)
logging = 'debug'
