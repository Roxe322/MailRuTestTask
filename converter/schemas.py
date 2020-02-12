from typing import Union

from marshmallow import Schema, fields, ValidationError
from marshmallow.validate import OneOf


class ConvertQuerySchema(Schema):
    """Query params schema for currency conversion."""

    from_ = fields.Str(description='Currency from which to convert',
                       required=True,
                       data_key='from')
    to = fields.Str(description='Currency to which to convert', required=True)
    amount = fields.Number(description='Amount of currency to convert',
                           required=True)


class InsertQuerySchema(Schema):
    """Query params schema for currencies inserting."""
    merge = fields.Int(required=True, validate=OneOf([0, 1]))


def validate_currency_rate(currency_rate: Union[int, float]):
    """
    Validates that only positive not null values could be currency rates.

    :param currency_rate Number which we supposed to be positive and not null
    """
    if currency_rate <= 0:
        raise ValidationError(
            "Only positive not null values could be currency rates"
        )


class InsertBodySchema(Schema):
    """JSON Body params for currencies inserting."""
    currencies = fields.Dict(
        description='Dictionary where keys are currencies '
                    'names and values are their rates',
        keys=fields.Str(description='Currencies names'),
        values=fields.Number(description='Currencies rates',
                             validate=validate_currency_rate),
        required=True
    )
