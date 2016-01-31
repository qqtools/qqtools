#!/bin/bash
# qqtools runner
#
# This file should be sourced rather than executed in a subshell,
# since some qqtools scripts are meant to modify environment variables
# or set the current directory. The easiest way is to set up a Bash alias.

if [ -z "$QQTOOLS_HOME" ]; then
  echo The QQTOOLS_HOME environment variable must be set.
fi

QQTOOLS_OUTPUT_SCRIPT=$(PYTHONPATH="$QQTOOLS_HOME" python -m qq.mktemp)

(
  QQTOOLS_CONFIG="$QQTOOLS_HOME/config"

  # Attempt to create qqtools home directory
  mkdir -p "$QQTOOLS_HOME/cmd"
  mkdir -p "$QQTOOLS_HOME/data"
  touch "$QQTOOLS_CONFIG"
  source "$QQTOOLS_CONFIG"

  export QQTOOLS_OUTPUT_SCRIPT
  PYTHONPATH="$QQTOOLS_HOME" python -m qq.cli $*
  exit $?
)

if [ -r "$QQTOOLS_OUTPUT_SCRIPT" ]; then
  source "$QQTOOLS_OUTPUT_SCRIPT"
  rm -f "$QQTOOLS_OUTPUT_SCRIPT"
fi

unset QQTOOLS_OUTPUT_SCRIPT
