from math import degrees
import sys
import os

from src.interpreter import run
from src.__init__ import __version__


def shell(debug_mode=False):
    print(f'Cyan {__version__} shell on {sys.platform}')
    while True:
        try:
            text = input('>>> ')
        except KeyboardInterrupt:
            print('\nExiting...'); sys.exit(0)
        
        result, error = run('<stdin>', text, debug_mode=debug_mode)

        if error:
            print(error)
        else:
            print(result)


def run_file(filename, debug_mode):
    with open(filename) as file:
        text = file.read()

    result, error = run(filename, text, debug_mode=debug_mode)

    if error:
        print(error)
    else:
        print(result)


def main():
    """
    -d
    --version
    --help
    file
    """
    debug = False
    argv = sys.argv[1:]
    if '-d' in argv:
        debug = True
        argv.remove('-d')
    if not argv:
        shell(debug_mode=debug)
        return
    if '--version' in argv:
        print(__version__)
        return
    if '--help' in argv:
        print(f"Cyan {__version__}")
        print(f"")
        print(f"    --version    See Cyan version")
        print(f"    --help       See this message")
        print(f"    -d           Enable debug mode")
        return
    for arg in argv:
        if os.path.exists(arg):
            run_file(arg, debug_mode=debug)

    
if __name__ == '__main__':
    main()
