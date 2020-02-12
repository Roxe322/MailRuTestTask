import pytest

from converter.db import KEY_PREFIX


async def test_only_number_rates_could_be_inserted(client):
    """Tests that only number rates сould be inserted."""
    response = await client.post(
        client.app.router['insert'].url_for(),
        params={'merge': 0},
        json={'currencies': {'CUR': 'abc'}}
    )

    assert response.status == 422

    json_response = await response.json()
    assert json_response['currencies']['CUR']['value'] == [
        'Not a valid number.'
    ]


@pytest.mark.parametrize('value', [-1, 0, -2.5])
async def test_only_positive_rates_could_be_inserted(client, value):
    """Tests that only positive rates сould be inserted."""
    response = await client.post(
        client.app.router['insert'].url_for(),
        params={'merge': 0},
        json={'currencies': {'CUR': value}}
    )

    assert response.status == 422

    json_response = await response.json()
    assert json_response['currencies']['CUR']['value'] == [
        'Only positive not null values could be currency rates.'
    ]


async def test_inserting_without_merging(client):
    """Tests that new currency rates added succesfully and all old invalidates."""
    await client.app['db'].set(f'{KEY_PREFIX}:RUB', 1.0)

    new_currency_name = 'CUR'
    new_currency_rate = 25.0

    response = await client.post(
        client.app.router['insert'].url_for(),
        params={'merge': 0},
        json={'currencies': {new_currency_name: new_currency_rate}}
    )

    assert response.status == 201
    all_currencies_in_db = await client.app['db'].keys(f'{KEY_PREFIX}:*')
    assert all_currencies_in_db == [
        bytes(f'{KEY_PREFIX}:{new_currency_name}', encoding='utf-8')
    ]
    rate = await client.app['db'].get(f'{KEY_PREFIX}:{new_currency_name}')
    assert rate == bytes(str(new_currency_rate), encoding='utf-8')


async def test_inserting_with_merging(client):
    """Tests that new currencies updates old ones."""
    rub_rate = 1.0
    await client.app['db'].set(f'{KEY_PREFIX}:RUB', rub_rate)
    await client.app['db'].set(f'{KEY_PREFIX}:USD', 60.0)
    new_usd_rate = 30.0  # Get back 2007

    response = await client.post(
        client.app.router['insert'].url_for(),
        params={'merge': 1},
        json={'currencies': {'USD': new_usd_rate}}
    )

    assert response.status == 201

    all_currencies_in_db = await client.app['db'].keys(f'{KEY_PREFIX}:*')

    assert set(all_currencies_in_db) == {
        bytes(f'{KEY_PREFIX}:USD', encoding='utf-8'),
        bytes(f'{KEY_PREFIX}:RUB', encoding='utf-8')
    }

    usd_rate = await client.app['db'].get(f'{KEY_PREFIX}:USD')
    old_rub_rate = await client.app['db'].get(f'{KEY_PREFIX}:RUB')
    assert usd_rate == bytes(str(new_usd_rate), encoding='utf-8')
    assert old_rub_rate == bytes(str(rub_rate), encoding='utf-8')
