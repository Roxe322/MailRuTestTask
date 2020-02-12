from typing import Dict

from aiohttp import web
from webargs.aiohttpparser import use_kwargs

from converter import db
from converter.schemas import ConvertQuerySchema, InsertBodySchema, InsertQuerySchema


@use_kwargs(ConvertQuerySchema())
async def convert(request: web.Request, from_: str, to: str, amount: float) -> web.Response:
    """
    Handler for converting currencies.

    :param request aiohttp request object
    :param from_ Currency from which to convert
    :param to Currency to which to convert
    :param amount Amount of `from_` currency to be converted
    """
    try:
        result = await db.convert(request.app['db'], from_.upper(), to.upper(), amount)
    except db.NoSuchCurrency as error:
        return web.json_response({'error': str(error)}, status=web.HTTPNotFound.status_code)

    return web.json_response({'result': result})


@use_kwargs(InsertBodySchema(), locations=['json'])
@use_kwargs(InsertQuerySchema(), locations=['query'])
async def insert(request: web.Request, currencies: Dict[str, float], merge: int):
    """
    Handler for updating currencies rates.

    :param request aiohttp request object
    :param currencies dict where keys are currencies names and values are their rates
    :param merge Should we merge old and new values or not, represented as 0/1 value
    """
    await db.insert(request.app['db'], currencies, bool(merge))

    return web.json_response({'ok': 'ok'})