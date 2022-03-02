from src.interpreter import run
import time
from src.__init__ import __version__

import sys


DEBUG = 0


def shell():
    print(f'Cyan {__version__}')
    try:

        while True:
            text = input('&> ')
            result, error = run('<stdin>', text, debug_mode=DEBUG)

            if error:
                print(error)
            else:
                print(result)

    except KeyboardInterrupt:
        print('Exiting...')
        time.sleep(1)


def run_file(filename):
    with open(filename) as file:
        text = file.read()

    result, error = run(filename, text, debug_mode=DEBUG)

    if error:
        print(error)
    else:
        print(result)


if __name__ == '__main__':
    argv = sys.argv[1:]
    if len(argv) and argv[0] == 'd':
        DEBUG = True
    shell()
