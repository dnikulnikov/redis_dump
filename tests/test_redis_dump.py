import pytest


@pytest.mark.asyncio
async def test_redis_dump_init(ro):
    assert ro._types == set(['string', 'list', 'set', 'zset', 'hash'])
    assert ro._have_pttl is False
