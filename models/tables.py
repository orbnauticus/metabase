
import datetime


def function_url(controller, function, *args):
    def urls(id):
        return URL(controller, function, args=filter(None, (id,) + args))
    return urls


_Field = Field


def Field(name, type='string', *args, **kwargs):
    null_value = kwargs.pop('null_value', '')
    primary = kwargs.pop('primary', False)
    if primary:
        kwargs['unique'] = True
        kwargs['required'] = True
    if kwargs.pop('automatic', False):
        kwargs['writable'] = False
    field = _Field(name, type, *args, **kwargs)
    if type.startswith('reference '):
        referenced = type.partition(' ')[2]
        table = getattr(db, referenced)
        table._extra['related'].append(field)
    field.extra = dict(
        null_value=null_value,
        primary=primary,
    )
    return field


class MB(object):

    def __init__(self, db):
        self.db = db
        self.handlers = dict()

    def wrap_table(self, table, function, index, **kwargs):
        self.handlers[function] = table
        primary = kwargs.pop('primary', None) or []
        if primary:
            for field in primary:
                if isinstance(field, str):
                    field = table[field]
                if not hasattr(field, 'extra'):
                    field.extra = dict()
                field.extra['primary'] = True
        for field in table:
            if (hasattr(field, 'extra') and
                    field.extra.get('primary') and
                    field.name not in primary):
                primary.append(field.name)
        if primary:
            table._format = ' '.join(['%%(%s)s' % name for name in primary])
        table._extra = dict(
            urls=None,
            index=index,
            function=function,
            primary=primary,
            related=[],
            columns=kwargs.get('columns') or [],
        )

    def define_table(self, name, function, index, *fields, **kwargs):
        properties = dict(kwargs)
        properties.pop('columns', None)
        self.db.define_table(name, *fields, **properties)
        return self.wrap_table(
            getattr(self.db, name), function, index,
            **kwargs)


mb = MB(db)

mb.define_table('organizations', 'organization', 1,
    Field('name', 'string', primary=True),
)

mb.wrap_table(db.auth_user, 'user', 3,
              primary=['username'],
              columns=['id', 'username', 'first_name', 'last_name', 'email'])

mb.define_table('org_membership', 'membership', 2,
    Field('organization', 'reference organizations'),
    Field('user', 'reference auth_user'),
)

mb.wrap_table(db.auth_group, 'group', 2,
              primary=['role'],
              columns=['id', 'role', 'description'])

mb.define_table('objects', 'object', 10,
    Field('name', 'string', primary=True),
    Field('created', 'datetime', default=datetime.datetime.now),
    Field('created_by', 'reference auth_user', default=auth.user),
    Field('modified', 'datetime', update=datetime.datetime.now),
    Field('modified_by', 'reference auth_user', update=auth.user),
    columns=['id', 'name', 'created_by', 'created', 'modified_by', 'modified'],
)

mb.define_table('datatypes', 'datatype', 11,
    Field('name', 'string', primary=True),
    Field('db_type', 'string', requires=IS_IN_SET(['string', 'integer'])),
)

mb.define_table('fields', 'field', 12,
    Field('object', 'reference objects'),
    Field('name', 'string', primary=True),
    Field('datatype', 'reference datatypes'),
    columns=['id', 'object', 'name'],
)

mb.define_table('records', 'record', 100,
    Field('name', 'string', primary=True),
)