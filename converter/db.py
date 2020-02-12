from typing import Optional, Dict

import aioredis
from aiohttp.web import Application

KEY_PREFIX = 'converter'


class NoSuchCurrency(Exception):
    """Custom exception to handle cases when one or both
    currencies don't exist."""


async def init_db(app: Application) -> None:
    """
    Initializes redis pool and sets it to app.

    :param app: Application object
    """
    config = app['config'].redis
    redis = await aioredis.create_redis_pool(
        f'redis://{config.host}:{config.port}', db=config.database
    )
    app['db'] = redis


async def stop_db(app: Application) -> None:
    """
    Clears redis connection pool.

    :param app: Application object
    """
    db = app['db']
    db.close()
    await db.wait_closed()


async def convert(db: aioredis.Redis,
                  from_: str,
                  to: str,
                  amount: float) -> Optional[float]:
    """
    Converts amount of currency from one to another.

    :param db: Redis interface
    :param from_: Currency from which to convert
    :param to: Currency to which to convert
    :param amount: How much `from_` currency to convert

    :return Amount of `from` currency converted to `to` currency

    :raises NoSuchCurrency: If any currency doesn't exist.

    """
    currency_from_rate, currency_to_rate = await db.mget(
        f"{KEY_PREFIX}:{from_}", f"{KEY_PREFIX}:{to}"
    )
    non_existed_currencies = [
        name for name, rate in (
            (from_, currency_from_rate), (to, currency_to_rate)
        ) if rate is None
    ]

    if non_existed_currencies:
        message = ', '.join(non_existed_currencies)
        raise NoSuchCurrency(f'Currencies do not exist: {message}.')

    return amount * float(currency_from_rate) / float(currency_to_rate)


async def insert(db: aioredis.Redis,
                 currencies: Dict[str, float], merge: bool) -> None:
    """
    Inserts new currency rates.

    :param db: Redis interface
    :param currencies: dict where keys are currencies names and
    values are their rates
    :param merge If True, invalidates all old values

    """
    if not merge:
        currencies_to_delete = await db.keys(f"{KEY_PREFIX}:*")
        await db.delete(*currencies_to_delete)

    currencies = {
        f"{KEY_PREFIX}:{currency.upper()}": rate
        for currency, rate in currencies.items()
    }  # We do not do any validation here because it all put to Marshmallow

    await db.mset(currencies)
