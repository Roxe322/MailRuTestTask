import logging

from aiohttp import web

from converter.db import init_db, stop_db
from converter.routes import setup_routes
from converter.settings import get_config


def init_app(config_file_name: str) -> web.Application:
    """Initializes and returns application.

    :param config_file_name Name of yaml file in config folder from
    which config will be loaded

    :return aiohttp Application object
    """
    app = web.Application()
    app['config'] = get_config(config_file_name)

    log_level = getattr(logging, app['config'].log_level, logging.INFO)
    logging.basicConfig(level=log_level)

    app.on_startup.append(init_db)
    app.on_cleanup.append(stop_db)

    setup_routes(app)

    return app


def run_app(config_file_name: str) -> None:
    """
    Runs application.

    :param config_file_name Name of yaml file in config folder from
    which config will be loaded
    """
    app = init_app(config_file_name)
    web.run_app(app, host=app['config'].host, port=app['config'].port)
