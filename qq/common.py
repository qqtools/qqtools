"""
Common QQTools functionality that can be shared by scripts.
"""

from __future__ import print_function

import os
import imp
import inspect

from os import path

qq_dir = path.dirname(path.dirname(path.abspath(__file__)))

# Scripts folder is (from this file) ../scripts/
command_dir = path.join(qq_dir, 'cmd')

# Data folder is ../data/
data_dir = path.join(qq_dir, 'data')

_command_cache = None


class QQBadInvocation(RuntimeError):
    """
    Exception class to be raised when a command is invoked improperly.
    """
    pass


class QQCommand(object):
    """
    Base class for all QQTools commands.
    """

    # Commands must have a name in order to be registered
    name = None

    # fullpath is set during loading
    fullpath = None

    # Commands should have a short description less than 40 characters long
    shorttext = ""

    def execute(*args, **kwargs):
        """Execute this command."""
        raise NotImplementedError()

    def help(self):
        """Return help text about this command."""
        return "No help available."


def is_debug():
    """Returns True if the QQDEBUG environment variable is set."""
    return os.environ.get('QQDEBUG', None) is not None


def shell_execute(cmd):
    """Execute a bash command inside the calling shell."""
    script = os.environ.get('QQTOOLS_OUTPUT_SCRIPT', None)
    if script is None:
        print('QQTOOLS_OUTPUT_SCRIPT is not set. Cannot execute in calling shell.')
    with open(script, 'a') as f:
        print(cmd, file=f)


def find_commands(cache=True):
    """
    Scans the script directory and extracts all commands.
    """
    global _command_cache
    if _command_cache is not None and cache:
        return _command_cache

    files = os.walk(command_dir)
    commands = {}
    for (dirpath, dirnames, filenames) in files:
        for filename in filenames:
            fullpath = path.join(dirpath, filename)
            if path.isfile(fullpath) and filename.endswith('py'):
                # Attempt to load the script and extract any QQCommands
                mod_name, ext = path.splitext(filename)
                try:
                    mod = imp.load_source(mod_name, fullpath)
                    for name in dir(mod):
                        obj = getattr(mod, name)
                        cmd_name = getattr(obj, 'name', None)
                        if cmd_name is not None and QQCommand in getattr(obj, '__mro__', []):
                            obj.fullpath = fullpath
                            commands[cmd_name] = obj
                except Exception as e:
                    print('Warning: failed attemping to load script "{}"'.format(filename))
                    print('Extended failure information:')
                    print(e)
    _command_cache = commands
    return commands


def instantiate_command(command_name):
    """
    Get an object instance for a QQCommand with the given name.
    """
    commands = find_commands()
    if command_name in commands:
        command = commands[command_name]
        inst = command()
        return inst
    return None


def get_data_filename(filename):
    """
    Get a filename within the QQTools data directory.
    """
    try:
        os.makedirs(data_dir)
    except OSError:
        pass
    return path.join(data_dir, filename)


def output(*args, **kwargs):
    print(*args, **kwargs)


def debug(*args, **kwargs):
    if is_debug():
        print(*args, **kwargs)
