"""
Core QQTools commmands.
"""

import qq
import re


class ListCommands(qq.QQCommand):
    """
    Command for listing available commands.
    """

    name = 'ls'
    shorttext = 'List available commands'

    def execute(self, pattern=None):
        commands = qq.find_commands()
        pattern = pattern or '.*'
        qq.output('Commands matching the pattern ' + pattern + ':')
        found = False
        for key in sorted(commands.iterkeys()):
            if re.match(pattern, key):
                found = True
                qq.output(' * {0} ({1})'.format(key, commands[key].shorttext))
        if not found:
            print(' No commands found.')
        return True

    def help(self):
        return '''Usage: qq ls [PATTERN]
Return a list of every command available, optionally matching the given
regular expression pattern.
        '''


class Help(qq.QQCommand):
    """
    Command for showing help on a command.
    """

    name = 'help'
    shorttext = 'Get help on a command'

    def execute(self, command_name):
        try:
            inst = qq.instantiate_command(command_name)
        except Exception as e:
            qq.output('Failed to instantiate command: ' + command_name)
            qq.output(e)
        qq.output(inst.help())
        return True

    def help(self):
        return '''Usage: qq help COMMAND
Display help information about a particular command.
        '''
