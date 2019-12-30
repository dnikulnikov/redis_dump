import time
import argparse
import ast
import re
from redis import StrictRedis as Redis


class RedisDump(Redis):

    def __init__(self, *a, **kw):
        Redis.__init__(self, *a, **kw)
        version = [
            int(part) for part in self.info()['redis_version'].split('.')]
        self._have_pttl = version >= [2, 6]
        self._types = set(['string', 'list', 'set', 'zset', 'hash'])

    def get_one(self, key):
        type = self.type(key)
        p = self.pipeline()
        p.watch(key)
        p.multi()
        p.type(key)
        if self._have_pttl:
            p.pttl(key)
        else:
            p.ttl(key)
        if type == b'string':
            p.get(key)
        elif type == b'list':
            p.lrange(key, 0, -1)
        elif type == b'set':
            p.smembers(key)
        elif type == b'zset':
            p.zrange(key, 0, -1, False, True)
        elif type == b'hash':
            p.hgetall(key)
        elif type == b'none':
            print('Skipping None value!', key)
            return None
        else:
            raise TypeError('Unknown type=%r' % type)
        type2, ttl, value = p.execute()
        if self._have_pttl and ttl > 0:
            ttl = ttl / 1000.0
        if type != type2:
            raise TypeError('Type changed')
        if ttl > 0:
            expire_at = time.time() + ttl
        else:
            expire_at = -1
        return type, key, ttl, expire_at, value

    def pattern_iter(self, pattern='*'):
        for key in self.keys(pattern):
            res = self.get_one(key)
            if res:
                yield res

    def dump(self, outfile, pattern='*', ns_old=None, ns_new=None):
        for type, key, ttl, expire_at, value in self.pattern_iter(pattern):
            if ns_old and ns_new:
                key = key.decode()
                key = re.sub(r"^{}\.".format(ns_old),
                             '{}.'.format(ns_new), key)
                key = key.encode()
            line = repr((type, key, ttl, expire_at, value,))
            outfile.write(line + '\n')

    def set_one(self, p, use_ttl, key_type, key, ttl, expire_at, value):
        p.delete(key)
        if key_type == b'string':
            p.set(key, value)
        elif key_type == b'list':
            for element in value:
                p.rpush(key, element)
        elif key_type == b'set':
            for element in value:
                p.sadd(key, element)
        elif key_type == b'zset':
            for element, score in value:
                p.zadd(key, score, element)
        elif key_type == b'hash':
            p.hmset(key, value)
        else:
            raise TypeError('Unknown type=%r' % type)
        if ttl <= 0:
            return
        if use_ttl:
            if type(ttl) is int:
                p.expire(key, ttl)
            else:
                p.pexpire(key, int(ttl * 1000))
        else:
            if type(expire_at) is int:
                p.expireat(key, expire_at)
            else:
                p.pexpireat(key, int(expire_at * 1000))

    def restore(self, infile, use_ttl=False, bulk_size=1000):
        cnt = 0
        p = self.pipeline(transaction=False)
        dirty = False
        for i, line in enumerate(infile):
            line = line.strip()
            if not line:
                continue
            a = ast.literal_eval(line)
            if len(a) != 5:
                raise ValueError(
                    'expecting type, key, ttl, expire_at, value got %r' % a)
            type, key, ttl, expire_at, value = a
            self.set_one(p, use_ttl, type, key, ttl, expire_at, value)
            dirty = True
            if i % bulk_size == 0:
                dirty = False
                p.execute()
                p = self.pipeline(transaction=False)
            cnt += 1
        if dirty:
            p.execute()
        return cnt


def main():
    DESCR = 'Скрипт для переноса базы redis'
    parser = argparse.ArgumentParser(description=DESCR)
    parser.add_argument(
        '--from_host',
        required=True,
        help='Обязательный. redis from host.'
    )
    parser.add_argument(
        '--from_port',
        required=True,
        help='Обязательный. redis form port'
    )
    parser.add_argument(
        '--from_namespace',
        required=True,
        help='Обязательный. redis from namespace'
    )
    parser.add_argument(
        '--to_host',
        required=True,
        help='Обязательный. redis to host. '
    )
    parser.add_argument(
        '--to_port',
        required=True,
        help='Обязательный. redis to port'
    )
    parser.add_argument(
        '--to_namespace',
        required=True,
        help='Обязательный. redis to namespace'
    )
    args, extra = parser.parse_known_args()

    r1 = {
        'host': args.from_host,
        'port': int(args.from_port),
        'namespace': args.from_namespace,
    }
    r2 = {
        'host': args.to_host,
        'port': int(args.to_port),
        'namespace': args.to_namespace,
    }
    try:
        filename = './dump_file.txt'
        ro1 = RedisDump(host=r1['host'], port=r1['port'])
        with open(filename, 'w+') as outfile:
            ro1.dump(
                outfile,
                '{}.*'.format(r1['namespace']),
                r1['namespace'],
                r2['namespace'])

        ro2 = RedisDump(host=r2['host'], port=r2['port'])
        with open(filename, 'r+') as infile:
            cnt = ro2.restore(infile)
    except Exception as e:
        print('ERROR:', e)

    print('Success', cnt)
