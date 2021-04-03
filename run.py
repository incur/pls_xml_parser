# This is a sample Python script.
from app.tests import main
from app.tools.tools import timeit
from app.config import clean_startup


@timeit
def run():
    clean_startup()
    main()


if __name__ == '__main__':
    run()
