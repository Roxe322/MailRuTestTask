import pytest

from converter.db import KEY_PREFIX


@pytest.mark.parametrize('params', (
    {'from': 'a'},
    {'from': 'a', 'to': 'b'},
    {'from': 'a', 'amount': 1},
    {'to': 'a'},
    {'to': 'a', 'amount': 1},
    {'amount': 1},
))
async def test_convert_handler_required_params_validation(client, params):
    """Tests that server responses 422 and provides full error info if any of
    required parameters was not provided."""
    all_fields = ('from', 'to', 'amount')
    empty_fields = [field for field in all_fields if field not in params]

    response = await client.get(
        client.app.router['convert'].url_for(), params=params
    )
    json_response = await response.json()

    assert response.status == 422
    for field in empty_fields:
        assert field in json_response
        assert json_response[field] == ['Missing data for required field.']


async def test_convert_handler_if_currency_does_not_exist(client):
    """Tests that server responses 404 and provides full error info if any of
    currency does not exist."""
    exist_currency = 'ABC'
    await client.app['db'].set(f'{KEY_PREFIX}:ABC', 1.0)

    non_exist_currency = 'B'

    response = await client.get(
        client.app.router['convert'].url_for(),
        params={'from': exist_currency, 'to': non_exist_currency, 'amount': 1})
    json_response = await response.json()

    assert response.status == 404

    assert 'error' in json_response
    assert json_response['error'] == (f'Currencies do not '
                                      f'exist: {non_exist_currency}.')


async def test_convert_handler_params_validation(client):
    """Tests that not Number can't be amount value."""
    response = await client.get(
        client.app.router['convert'].url_for(), params={'from': 'a',
                                                        'to': 'b',
                                                        'amount': 'TEST'})
    assert response.status == 422

    json_response = await response.json()
    assert 'amount' in json_response
    assert json_response['amount'] == ['Not a valid number.']


@pytest.mark.parametrize('from_,to,amount,result', [
        ('RUB', 'USD', 180, 3),
        ('USD', 'rub', 2, 120),
        ('rUb', 'usd', 30, 0.5),
])
async def test_conversion(client, from_, to, amount, result):
    """Tests conversion results with valid params."""
    await client.app['db'].set(f'{KEY_PREFIX}:RUB', 1.0)
    await client.app['db'].set(f'{KEY_PREFIX}:USD', 60)

    response = await client.get(
        client.app.router['convert'].url_for(), params={'from': from_,
                                                        'to': to,
                                                        'amount': amount})
    assert response.status == 200
    json_response = await response.json()
    assert 'result' in json_response
    assert json_response['result'] == result

