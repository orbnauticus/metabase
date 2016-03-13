# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

response.view = 'default/index.html'


def readable_id(id):
    return id.replace('_', ' ').title()


class Bijection(dict):
    def __init__(self, mapping=None):
        super(Bijection, self).__init__()
        if mapping:
            for key in mapping:
                self[key] = mapping[key]

    def __setitem__(self, key, value):
        super(Bijection, self).__setitem__(key, value)
        super(Bijection, self).__setitem__(value, key)

    def __delitem__(self, key):
        value = self[key]
        super(Bijection, self).__delitem__(key)
        super(Bijection, self).__delitem__(value)


class a62:
    mapping = Bijection({j: i for j, i in zip(
        range(62),
        '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    )})
    base = 62

    @classmethod
    def encode(cls, value, length):
        return ''.join([
            cls.mapping[x] for x in (
                (value // cls.base**i) % cls.base
                for i in range(length - 1, -1, -1)
            )
        ])

    @classmethod
    def decode(cls, text):
        return sum(
            cls.mapping[c] * cls.base**(len(text)-i-1)
            for i, c in enumerate(text)
        )


class ListView:
    def __init__(self, table, names, query=None, orderby=None, title=None,
                 controller=None, function=None):
        self.table = table
        self.names = names
        self.query = query or (self.table.id > 0)
        self.orderby = orderby or self.table.id
        self.title = title or readable_id(table._id.tablename)
        self.controller = controller or request.controller
        self.function = function or request.function

    def headers(self):
        for name in self.names:
            yield readable_id(name) if name != 'id' else XML('&nbsp;')

    def columns(self):
        for name in self.names:
            yield self.table[name]

    def rows(self):
        properties = dict(
            orderby=self.orderby,
        )
        return db(self.query).select(*self.columns(), **properties)

    def view_url(self, id):
        return URL(self.controller, self.function, args=[id])

    def edit_url(self, id):
        return URL(self.controller, self.function, args=[id, 'edit'],
                   vars={'next': request.env.path_info})

    def delete_url(self, id):
        return URL(self.controller, self.function, args=[id, 'delete'],
                   vars={'next': request.env.path_info})

    def new_url(self):
        return URL(self.controller, self.function, args=['new'])


class Form:
    def __init__(self, table, record=None, default_redirect=None):
        self.form = SQLFORM(table, record)
        self.default_redirect = default_redirect

    def process(self):
        if self.form.process().accepted:
            redirect(request.get_vars.next or
                     self.default_redirect(self.form.vars))
        return self.form


class Itemview:
    def __init__(self, table, record):
        self.table = table
        self.record = record


def delegate(table, first, second, list_columns, list_orderby,
             default_redirect):
    record = table(first)
    verb = first if record is None else second
    if record is None and verb is None:
        response.view = 'listview.html'
        return dict(listview=ListView(table, list_columns, orderby=list_orderby))
    elif record is None and verb == 'new' or verb == 'edit':
        response.view = 'form.html'
        return dict(
            form=Form(table, record, default_redirect=default_redirect).process(),
        )
    elif record and verb is None:
        response.view = 'itemview.html'
        return dict(itemview=Itemview(table, record))
    elif record and verb == 'delete':
        return dict()
    raise HTTP(404)


class Delegate(dict):

    handlers = dict(
        object=dict(
            id=10,
            table=db.objects,
            columns=['id', 'name', 'created_by', 'created', 'modified_by',
                     'modified'],
        ),
        user=dict(
            id=1,
            table=db.auth_user,
            columns=['id', 'username', 'first_name', 'last_name', 'email'],
        ),
        group=dict(
            id=2,
            table=db.auth_group,
            columns=['id', 'role', 'description'],
        ),
        field=dict(
            id=11,
            table=db.fields,
            columns=['id', 'object', 'name'],
        ),
    )

    def __init__(self, first, second, function=None):
        self.function = function or request.function
        handler = self.handlers[self.function]
        self.table = handler['table']
        self.list_orderby = self.table._extra['primary']
        self.list_columns = handler['columns']
        dict.__init__(self, display=self.display)
        self['url'] = self.url
        record = self.table(first)
        verb = first if record is None else second
        if record and verb is None:
            self['itemview'] = self.build_itemview(record)
        elif record is None and verb is None:
            self['listview'] = self.build_listview()
        elif record is None and verb == 'new' or verb == 'edit':
            self['form'] = self.build_form(record)
        elif record and verb == 'delete':
            self['form'] = self.build_delete()
        else:
            raise HTTP(404)

    def display(self, field, row):
        text = row[field]
        link = ''
        type, is_reference, table_name = field.type.partition(' ')
        if type == 'reference' and text is not None:
            table = db[table_name]
            reference = text
            text = (table._format(table[text]) if callable(table._format)
                     else table._format % table[text].as_dict())
            if 'urls' in table._extra:
                link = self.url(table._extra['function'], reference)
        elif field.represent is not None:
            text = field.represent(text, row)
        if text is None and hasattr(field, 'extra') and 'null_value' in field.extra:
            text = field.extra['null_value']
        if hasattr(field, 'extra') and field.extra.get('primary'):
            link = self.url(field.table._extra['function'], row.id)
        if link:
            return A(text, _title=text, _href=link, _class=type)
        else:
            return SPAN(text, _title=text, _class=type)

    @classmethod
    def from_request(cls):
        self = cls(request.args(0), request.args(1))
        return self

    @staticmethod
    def default_redirect(vars):
        return URL(request.controller, request.function, args=[vars.id])

    def build_itemview(self, record):
        return Itemview(self.table, record)

    def build_listview(self):
        return ListView(self.table, self.list_columns, orderby=self.list_orderby)

    def build_form(self, record):
        return Form(self.table, record, default_redirect=self.default_redirect)

    def build_delete(self):
        return

    @classmethod
    def url(cls, table, reference=None, verb=None):
        args = [a62.encode(cls.handlers[table]['id'], 4)]
        if reference is not None:
            args[0] += a62.encode(reference, 10)
        if verb:
            args.append(verb)
        return URL(r=request, args=args)


@auth.requires_login()
def index():
    tables = Bijection({Delegate.handlers[key]['id']: key
                        for key in Delegate.handlers})
    first = request.args(0)
    if first:
        if len(first) not in (4, 14):
            raise HTTP(404)
        function = tables.get(a62.decode(first[:4]), 'not found')
        reference = a62.decode(first[4:]) if first[4:] else None
        response.flash = CAT(
            'function: ', function, BR(),
            'reference: ', reference, BR(),
        )
        verb = {
            None: None,
            'e': 'edit',
            'd': 'delete',
        }[request.args(1)]
        return Delegate(reference, verb, function=function)
    second = request.args(1)
    # request.function = 'object'
    return Delegate(first, second, function='object')


@auth.requires_login()
def object():
    return Delegate.from_request()


@auth.requires_login()
def field():
    return Delegate.from_request()


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


'''
def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()
'''