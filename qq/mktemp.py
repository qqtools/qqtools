"""
Cross-platform mktemp replacement for QQTools
"""

from __future__ import print_function

import tempfile


def main():
    f, path = tempfile.mkstemp(prefix='qq-')
    print(path)


if __name__ == '__main__':
    main()
