"""
QQTools command-line runner.
"""

from __future__ import print_function

import sys
import os
import re

from os import path
from .common import instantiate_command, QQBadInvocation, is_debug



def usage():
    """
    Print application usage and exit.
    """

    print(
        'QQTools script runner\n'
        'Usage: qq <command> [arguments]\n'
        '\n'
        'Execute a command from the QQTools command directory.\n'
    )
    exit(1)


def main():
    if len(sys.argv) < 2:
        usage()
    command_name = sys.argv[1]

    try:
        inst = instantiate_command(command_name)
    except Exception as e:
        print('Failed to instantiate command: ' + command_name)
        print(e)
        if is_debug():
            raise
    if not inst:
        print('Command not found: ' + command_name)
        exit(1)
    try:
        inst.execute(*sys.argv[2:])
    except Exception as e:
        if isinstance(e, QQBadInvocation):
            print(inst.help())
            exit(1)
        # Kind of a hack (could catch arity errors that propagate from inside command)
        # but good enough
        if isinstance(e, TypeError) and re.match(r'.*takes (exactly|at least|at most) \d+ argument.*', str(e)):
            print(inst.help())
            exit(1)
        print('Unexpected failure in command: ' + command_name)
        print(e)
        if is_debug():
            raise

    except Exception as e:
        print('Unexpected error in command: ' + command_name)
        print('')
        print(e)
        if is_debug():
            raise


if __name__ == '__main__':
    main()
