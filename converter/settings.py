import pathlib

import yaml
from pydantic import BaseModel

BASE_DIR = pathlib.Path(__file__).parent.parent
CONFIG_PATH = str(BASE_DIR / 'config' / '{}.yaml')


class RedisConfig(BaseModel):
    """Internal Redis config representation."""
    host: str
    port: int
    database: int


class Config(BaseModel):
    """App config representation."""
    redis: RedisConfig
    host: str
    port: int
    log_level: str


def get_config(config_file_name: str) -> Config:
    """
    Loads and validates config.

    :param config_file_name Name of yaml file in config folder
    from which config will be loaded
    """
    config_path = CONFIG_PATH.format(config_file_name)

    with open(config_path) as config_file:
        config = yaml.safe_load(config_file)

    return Config(**config)
