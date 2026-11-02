"""예제 전체가 공유하는 Redis 연결, 키 상태 확인, 패턴 예제용 가짜 DB 헬퍼."""
import time

import redis

REDIS_URL = "redis://localhost:6379/0"


def connect(decode=True):
    """decode_responses=True면 응답을 bytes 대신 str로 받는다 (ex1 참고)."""
    return redis.Redis.from_url(REDIS_URL, decode_responses=decode, socket_connect_timeout=3)


def reset(r, prefix):
    """재실행해도 결과가 같도록 이 예제의 키(prefix:*)만 지운다."""
    keys = list(r.scan_iter(f"{prefix}:*"))
    if keys:
        r.delete(*keys)


def show(r, key):
    """키의 자료형·TTL·값을 한 줄로 보여준다. redis-cli의 TYPE/TTL/조회 명령과 같은 정보."""
    t = r.type(key)
    value = {
        "string": lambda: r.get(key),
        "list": lambda: r.lrange(key, 0, -1),
        "set": lambda: sorted(r.smembers(key)),
        "hash": lambda: r.hgetall(key),
        "zset": lambda: r.zrange(key, 0, -1, withscores=True),
        "none": lambda: None,
    }[t]()
    return f"{key} [{t}, ttl={r.ttl(key)}] {value}"


class FakeDB:
    """실무 패턴 예제에서 DB 대신 쓰는 dict. calls로 DB가 몇 번 호출됐는지 확인한다."""

    def __init__(self, data, delay=0.0):
        self.data = data
        self.delay = delay  # 느린 쿼리 흉내 (초)
        self.log = []  # list.append는 스레드 안전 → len(log)로 호출 수를 센다

    @property
    def calls(self):
        return len(self.log)

    def get(self, id):
        self.log.append(id)
        time.sleep(self.delay)
        return dict(self.data[id])

    def update(self, id, **fields):
        self.data[id].update(fields)
