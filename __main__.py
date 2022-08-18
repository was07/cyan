import sys

from src.interpreter import run
from src.__init__ import __version__


DEBUG = 0


def shell():
    print(f'Cyan {__version__} shell on {sys.platform}')
    while True:
        try:
            text = input('>>> ')
        except KeyboardInterrupt:
            print('\nExiting...'); sys.exit(0)
        
        result, error = run('<stdin>', text, debug_mode=DEBUG)

        if error:
            print(error)
        else:
            print(result)


def run_file(filename):
    with open(filename) as file:
        text = file.read()

    result, error = run(filename, text, debug_mode=DEBUG)

    if error:
        print(error)
    else:
        print(result)


def main():
    argv = sys.argv[1:]
    if argv[0] in ('-d', '--debug'):
        DEBUG = True
        argv = argv[1:]
    if argv[0] == ('--version'):
        print(__version__)
        sys.exit(0)
    if argv[0] == '--help':
        print(f'Usage: {sys.argv[0]} [options] [file]')
        print(f'Options:')
        print(f'  -d, --debug    Enable debug mode')
        print(f'  --version      Show version')
        print(f'  --help         Show this help')
        print(f'  file           Run the file')
        sys.exit(0)
    if len(argv) == 1:
        run_file(argv[0])
        sys.exit(0)

    shell()

    
if __name__ == '__main__':
    main()
