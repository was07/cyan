import os
import sys

from cyan import __version__
from cyan.interpreter import run, run_debug


def shell(debug_mode=False):
    print(f"Cyan {__version__} shell on {sys.platform}", end=" ")

    if debug_mode:
        _run_fn = run_debug
        print("[DEBUG MODE]")
    else:
        _run_fn = run
        print()

    while True:
        try:
            text = input(">>> ")

        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)

        if text.lstrip() == "":
            continue

        result, error = _run_fn("<stdin>", text)

        if error:
            print(error)
        else:
            print(result)


def run_file(filename: str, debug_mode: bool):
    with open(filename) as file:
        src = file.read()

    if debug_mode:
        res = run_debug(filename, src)
    else:
        res = run(filename, src)

    result, error = res

    if error is not None:
        print(error)


def main():
    """
    -d
    --version
    --help
    file
    """
    debug = False
    argv = sys.argv[1:]

    if "-d" in argv:
        debug = True
        argv.remove("-d")

    if not argv:
        shell(debug_mode=debug)

    if "--version" in argv:
        print(__version__)
        sys.exit(0)

    if "--help" in argv:
        print(f"Cyan {__version__}")
        print(f"")
        print(f"    --version    See Cyan version")
        print(f"    --help       See this message")
        print(f"    -d           Enable debug mode")
        sys.exit(0)

    for arg in argv:
        if os.path.exists(arg):
            run_file(arg, debug_mode=debug)


if __name__ == "__main__":
    main()
