# qqtools

qqtools allows command-line users to organize and execute
commands written in Python.

# Installation
1. Pick an installation location (your home directory, for example). The recommended directory name is `.qqd`.

```console
$ cd ~
$ git clone https://github.com/sbroadhead/qqtools.git
$ mv qqtools .qqd
```

2. Set the QQTOOLS_HOME environment variable in your `.bash_profile`:
```bash
export QQTOOLS_HOME=/home/user/.qqd
```

3. Set up a Bash alias to the command runner in your `.bash_profile`:
```bash
alias qq="source $QQTOOLS_HOME/qq.sh"
```

The alias is required, since qqtools commands may want to modify the current shell's environment (for example, to change the current directory). This is done by serializing shell commands to a temporary shell script and reading it using `source`, so the script runner itself must be `source`d as well, or else the effects would only apply to the sub-shell executing the script runner.

# Usage
Once qqtools is installed, simply invoke the `qq` alias to run a command.

```
qq COMMAND [ARGS...]
```

# Default Commands
By default the following commands are supplied:

 * `cmd.edit COMMAND` - Open the default editor (via `EDITOR` environment variable) to edit the file containing the command named NAME.
 * `help COMMAND` - Get help about a command by name
 * `ls [PATTERN]` - List all available commands, optionally filtered against a regexp pattern.
 * `tag [FOLDER] NAME` - Tag a folder with a name so it can be easily jumped back to later. If FOLDER is omitted, the current directory is used.
 * `tag.go NAME` - Change the current directory to the one tagged with the name NAME.
 * `tag.ls [PATTERN]` - List all tagged folders, optionally filtered against a regexp pattern.
 * `tag.rm NAME` - Untag the folder with the name NAME.

This is only a very small set of starter commands. New commands will be added as their development is warranted.

# Custom Commands
qqtools is written in Python and its commands are implemented as Python functions. Any file with the extension `.py` in the `.qqd/cmd` directory is automatically inspected for classes that derive from `qq.QQCommand`. The `qq` package is automatically available for import from any command scripts and contains common functionality used to implement qqtools commands. Subclasses should provide a `name` attribute and implementations of `execute` and `help`.

```python
class QQCommand(object):
    # Commands must have a name in order to be registered
    name = None

    # Commands should have a short description less than 40 characters long
    shorttext = ""

    def execute(*args, **kwargs):
        """Execute this command."""
        raise NotImplementedError()

    def help(self):
        """Return help text about this command."""
        # Subclasses should override this too
        return "No help available."
```

qqtools makes sure that a compatible number of arguments are supplied to the `execute` method, and responds with the help text if not.

## Basic command functionality
The `qq` module exports some helpful functions and classes for commands to use.

```python
import qq

# Print some text to the console
qq.output('Hello there')

# Get the name of a file relative to the .qqd/data directory
filename = qq.get_data_filename('names.sqlite3')
import sqlite3
conn = sqlite3.connect(filename)
# ....
conn.close()

# Instantiate another command by name
mycommand = qq.instantiate_command('mycommand')

# If the QQCommand object implementing 'mycommand' has a method
# called custom_method(), then we can call it here
foo = mycommand.custom_method()

# We can execute it directly as well, passing the arguments as
# though they were given on the command line
mycommand.execute('foo', 'bar')

# We can also get a dictionary of every available command, as a
# map from the command name to the QQCommand class implementing
# that command. We could reimplement the ls command using it:
all_commands = qq.find_commands()
for name, cmd in all_commands.itervalues():
    print '{0}: {1}'.format(name, cmd.shorttext)
```

## Executing in the calling shell
The `qq.shell_execute(cmd)` method is used to execute the command `cmd` in the environment of the calling shell (using `source`). For example,

```
qq.shell_execute('cd ~')
```

will cause the current directory to change to your home directory once the command has finished executing.

## Example command
Here is an example command that can evaluate and print a Python expression, as well as store it in an environment variable in the calling shell. Place this in `.qqd/cmd/eval_sample.py`:

```python
import qq

class Eval(qq.QQCommand):
    name = 'eval'
    shorttext = 'Evaluate a python expression'

    def execute(self, *args):
        cmd = ' '.join(args)
        qq.output('Evaluating {}...'.format(cmd))
        result = eval(cmd)
        qq.output(result)
        qq.shell_execute('EVAL_RESULT="{}"'.format(result))

    def help(self):
        return '''Usage: qq eval EXPRESSION
Evaluate a Python expression and place the result in the EVAL_RESULT
environment variable.'''
```

Example:

```console
$ qq eval "sum(xrange(1, 100))"
Evaluating sum(xrange(1, 100))...
4950
$ echo ${EVAL_RESULT}
4950
```
