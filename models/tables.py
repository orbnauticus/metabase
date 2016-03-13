
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

    def wrap_table(self, table, function, **kwargs):
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
            function=function,
            primary=primary,
            related=[],
        )

    def define_table(self, name, function, *fields, **kwargs):
        self.db.define_table(name, *fields, **kwargs)
        return self.wrap_table(getattr(self.db, name), function, **kwargs)


mb = MB(db)

mb.define_table('organizations', 'organization',
    Field('name', 'string', primary=True),
)

mb.wrap_table(db.auth_user, 'user', primary=['username'])

mb.define_table('org_membership', 'membership',
    Field('organization', 'reference organizations'),
    Field('user', 'reference auth_user'),
)

mb.wrap_table(db.auth_group, 'group', primary=['role'])

mb.define_table('datatypes', 'datatype',
    Field('name', 'string', primary=True),
    Field('db_type', 'string', requires=IS_IN_SET(['string', 'integer'])),
)

mb.define_table('objects', 'object',
    Field('created', 'datetime', default=datetime.datetime.now),
    Field('created_by', 'reference auth_user', default=auth.user),
    Field('modified', 'datetime', update=datetime.datetime.now),
    Field('modified_by', 'reference auth_user', update=auth.user),
    Field('name', 'string', primary=True),
)

mb.define_table('fields', 'field',
    Field('object', 'reference objects'),
    Field('name', 'string', primary=True),
    Field('datatype', 'reference datatypes'),
)

mb.define_table('records', 'record',
    Field('name', 'string', primary=True),
)