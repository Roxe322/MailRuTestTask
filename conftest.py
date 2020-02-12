import pytest

from converter.main import init_app
from converter.db import KEY_PREFIX


@pytest.fixture
async def client(loop, aiohttp_client):
    """Test app fixture."""
    app = init_app('test')
    yield await aiohttp_client(app)
    db = app['db']
    keys_to_delete = await db.keys(f"{KEY_PREFIX}:*")
    if keys_to_delete:
        await db.delete(*keys_to_delete)

