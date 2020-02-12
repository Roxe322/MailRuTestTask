import sys

from converter.main import run_app

if __name__ == '__main__':
    try:
        config_file_name = sys.argv[1]
    except IndexError:
        config_file_name = 'default'

    run_app(config_file_name)
