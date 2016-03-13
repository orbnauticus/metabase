# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.logo = A(B(SPAN('M'),'eta',SPAN('B'),'ase'),XML('&trade;&nbsp;'),
                  _class="navbar-brand",_href=URL('default', 'index'),
                  _id="web2py-logo")
response.title = request.application.replace('_',' ').title()
response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Ryan Marquardt <ryan.marquardt@gmail.com>'
response.meta.description = 'a cool new app'
response.meta.keywords = 'web2py, python, framework'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [
    (T('Home'), False, URL('default', 'index'), []),
    (T('Setup'), False, URL('setup', 'index'), []),
]

DEVELOPMENT_MENU = (auth.user and (auth.user.id == 1))

#########################################################################
## provide shortcuts for development. remove in production
#########################################################################

def PAedit(path):
    return ('https://www.pythonanywhere.com/user/integralws/files'
            '/home/integralws/glean/applications/metabase/%s?edit') % path

def _():
    # shortcuts
    app = request.application
    ctr = request.controller
    # useful links to internal and external resources
    response.menu += [
        (T('This App'), False, '#', [
            (T('Design'), False, URL('admin', 'default', 'design/%s' % app)),
            LI(_class="divider"),
            (T('Controller'), False, URL(
                'admin', 'default', 'edit/%s/controllers/%s.py' % (app, ctr))),
            (T('View'), False, URL(
                'admin', 'default', 'edit/%s/views/%s' % (app, response.view))),
            (T('DB Model'), False, URL(
                'admin', 'default', 'edit/%s/models/db.py' % app)),
            (T('Menu Model'), False, URL(
                'admin', 'default', 'edit/%s/models/menu.py' % app)),
            (T('Config.ini'), False, URL(
                'admin', 'default', 'edit/%s/private/appconfig.ini' % app)),
            (T('Layout'), False, URL(
                'admin', 'default', 'edit/%s/views/layout.html' % app)),
            (T('Stylesheet'), False, URL(
                'admin', 'default', 'edit/%s/static/css/web2py-bootstrap3.css' % app)),
            (T('Database'), False, URL(app, 'appadmin', 'index')),
            (T('Errors'), False, URL(
                'admin', 'default', 'errors/' + app)),
            (T('About'), False, URL(
                'admin', 'default', 'about/' + app)),
        ]),
    ]
if DEVELOPMENT_MENU: _()

if "auth" in locals(): auth.wikimenu()
