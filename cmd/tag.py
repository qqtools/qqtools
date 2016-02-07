"""
Commands for dealing with tagged folders.
"""
import collections

import qq
import os


class TagStorage(qq.Storage):
    def __init__(self):
        super(TagStorage, self).__init__('tags')
        if 'tags' not in self or not isinstance(self['tags'], collections.Mapping):
            self['tags'] = dict()


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

        tags = TagStorage()
        tags['tags'][name] = path
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
        tags = TagStorage()
        pattern = pattern or '.*'
        qq.output('Tagged folders matching the pattern {}:'.format(pattern))
        if len(tags['tags']) == 0:
            print(' No tags found.')
        else:
            for name, path in tags['tags'].iteritems():
                print(' * {0} ({1})'.format(name, path))
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
        tags = TagStorage()
        path = tags['tags'].pop(name, None)
        if path:
            qq.output('Untagged folder {} with name "{}"'.format(path, name))
        else:
            qq.output('Tag not found: ' + name)
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
        tags = TagStorage()
        if name not in tags['tags']:
            qq.output('Tag not found: ' + name)
            return False
        path = tags['tags'][name]
        qq.shell_execute('cd "{}"'.format(path))
        qq.output('Changing to tagged folder "{}" ({})'.format(name, path))
        return True

    def help(self):
        return '''Usage: qq tag.rm NAME
Delete the tagged folder named NAME.'''
