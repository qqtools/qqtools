"""
Simple data storage functionality via Sqlite.
"""

import sqlite3
import qq.common as qq
import re


def create_schema(conn, schema):
    """
    Create the schema in an Sqlite database if it does not already exist.
    """
    for table_name, table_def in schema.iteritems():
        sql = 'create table if not exists {0} ({1})'.format(
            table_name,
            ', '.join(field_name + ' ' + field_def for field_name, field_def in table_def)
        )
        qq.debug('Creating schema: ' + sql)
        conn.execute(sql)


def get_storage(name, schema=None):
    """
    Create a connection to an Sqlite database and optionally create the schema.
    The schema should be a dictionary mapping table names to a list of field definitions.
    The REGEXP operator is supported through Python's regular expression package.

    For example:

    schema = {
        'person': [
            ('id', 'primary key'),
            ('firstname', 'text'),
            ('lastname', 'text not null')
        ],
        'email': [
            ('id', 'primary key'),
            ('person_id', 'int references person(id)')
        ]
    }
    """
    conn = sqlite3.connect(qq.get_data_filename(name + '.sqlite3'))
    conn.row_factory = sqlite3.Row
    conn.isolation_level = None
    def regex(pattern, item):
        try:
            return re.match(pattern, item) is not None
        except Exception as e:
            return False
    conn.create_function('regexp', 2, regex)
    if schema is not None:
        create_schema(conn, schema)
    return conn
