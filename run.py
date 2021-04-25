import sys
from app import main, test


def run():
    main.main()


def run_test():
    test.main()


if __name__ == '__main__':
    arg = sys.argv
    if str(arg[1]) == 'test':
        run_test()
    else:
        run()
