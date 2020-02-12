from aiohttp.web import Application

from converter import views


def setup_routes(app: Application) -> None:
    """
    Setups application routes.

    :param app: aiohttp Application object
    """
    app.router.add_get('/convert/', views.convert, name='convert')
    app.router.add_post('/database/', views.insert, name='insert')
