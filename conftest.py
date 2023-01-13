from pytest import fixture
from loguru import logger


@fixture
def global_fixture():
    logger.info("\n(Doing global fixture setup stuff!)")