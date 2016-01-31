"""
Commands for dealing with tagged folders.
"""

import qq
import sqlite3
import contextlib
import os
import re


@contextlib.contextmanager
def database():
    conn = sqlite3.connect(qq.get_data_filename('tags.sqlite3'))
    conn.row_factory = sqlite3.Row
    conn.isolation_level = None
    conn.create_function('regexp', 2, lambda pattern, item: re.match(pattern, item) is not None)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tag (name text, path text)
    ''')
    yield conn
    conn.close()


class TagCommand(qq.QQCommand):
    """
    Tag a folder to return to later.
    """

    name = 'tag'
    shorttext = 'Tag a folder with a bookmark name'

    def execute(self, *args):
        if len(args) == 1:
            path = os.getcwd()
            name = args[0]
        elif len(args) == 2:
            path = args[0]
            name = args[1]
        else:
            raise qq.QQBadInvocation()
        with database() as conn:
            cur = conn.cursor()
            cur.execute('BEGIN TRANSACTION')
            cur.execute('DELETE FROM tag WHERE name = ?', (name,))
            cur.execute('INSERT INTO tag (name, path) VALUES (?, ?)', (name, path))
            cur.execute('COMMIT')
            qq.output('Tagged folder {} with name "{}".'.format(path, name))
        return True

    def help(self):
        return '''Usage: qq tag [FOLDER] NAME
Save the folder FOLDER under the name NAME. If FOLDER is omitted, then
the current working directory is used. Subsequently, use 'qq tag.go NAME' to jump to
the folder.'''


class ListTagsCommand(qq.QQCommand):
    """
    List tagged folders matching a regular expression pattern.
    """

    name = 'tag.ls'
    shorttext = 'List tagged folders'

    def execute(self, pattern=None):
        pattern = pattern or '.*'
        qq.output('Tagged folders matching the pattern {}:'.format(pattern))
        with database() as conn:
            cur = conn.cursor()
            found = False
            for row in cur.execute('SELECT name, path FROM tag WHERE name REGEXP ? ORDER BY name', (pattern,)):
                found = True
                qq.output(' * {0} ({1})'.format(row['name'], row['path']))
        if not found:
            print(' No tags found.')
        return True

    def help(self):
            return '''Usage: qq tag.ls [PATTERN]
List tagged folders, optionally filtering against a regular expression pattern.
'''


class DeleteTagCommand(qq.QQCommand):
    """
    Delete a tagged folder by name.
    """

    name = 'tag.rm'
    shorttext = 'Delete a tagged folder'

    def execute(self, name):
        with database() as conn:
            cur = conn.cursor()
            row = cur.execute('SELECT name, path FROM tag WHERE name = ?', (name,)).fetchone()
            if not row:
                qq.output('Tag not found: ' + name)
                return False
            cur.execute('BEGIN TRANSACTION')
            cur.execute('DELETE FROM tag WHERE name = ?', (name,))
            cur.execute('COMMIT')
            qq.output('Untagged folder {} with name "{}"'.format(row['path'], row['name']))
        return True

    def help(self):
        return '''Usage: qq tag.rm NAME
Delete the tagged folder named NAME.'''


class GoToTagCommand(qq.QQCommand):
    """
    Jump to a tagged folder.
    """

    name = 'tag.go'
    shorttext = 'Jump to a tagged folder'

    def execute(self, name):
        with database() as conn:
            cur = conn.cursor()
            row = cur.execute('SELECT name, path FROM tag WHERE name = ?', (name,)).fetchone()
            if not row:
                qq.output('Tag not found: ' + name)
                return False
            qq.shell_execute('cd "{}"'.format(row['path']))
            qq.output('Now in tagged folder "{}" ({})'.format(name, row['path']))
        return True

    def help(self):
        return '''Usage: qq tag.rm NAME
Delete the tagged folder named NAME.'''
