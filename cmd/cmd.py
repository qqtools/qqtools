"""
Commands for dealing with command scripts.
"""

import qq
import os


class EditCommand(qq.QQCommand):
    """
    Command for editing the file containing a command.
    """

    name = 'cmd.edit'
    shorttext = 'Edit a command'

    def execute(self, command_name):
        try:
            inst = qq.instantiate_command(command_name)
        except Exception as e:
            qq.output('Failed to instantiate command: ' + command_name)
            qq.output(e)
            return False
        if inst is None:
            qq.output('Command not found: ' + command_name)
            return False
        editor = os.environ.get('EDITOR', None)
        if editor is None:
            qq.output('The EDITOR environment variable is not set.')
            return False
        qq.shell_execute('"{}" "{}"'.format(editor, inst.fullpath))
        return True

    def help(self):
        return '''Usage: qq help COMMAND
Display help information about a particular command.
        '''
