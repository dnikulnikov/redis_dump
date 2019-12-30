from unittest import mock
import pytest
from redis_dump import RedisDump
from redis_dump import Redis


@pytest.fixture(scope='function')
def ro():
    Redis.__init__ = mock.MagicMock()
    RedisDump.connection = mock.MagicMock()
    RedisDump.connection_pool = mock.MagicMock()
    RedisDump.response_callbacks = mock.MagicMock()
    ro = RedisDump(host='http://localhost', port=6379)
    return ro
