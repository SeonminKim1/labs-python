"""ex10: [패턴 3] 분산 락 - SET NX EX, 토큰 확인 후 해제, redis-py Lock, 캐시 스탬피드 방지."""
import json
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

import redis

from common import FakeDB, connect, reset

r = connect()

# 내 토큰일 때만 삭제 - GET과 DEL 사이에 끼어들 수 없도록 Lua로 묶는다
RELEASE = r.register_script("""
if redis.call('GET', KEYS[1]) == ARGV[1] then
    return redis.call('DEL', KEYS[1])
end
return 0
""")


def acquire(name, ttl_ms):
    token = str(uuid.uuid4())
    return token if r.set(name, token, nx=True, px=ttl_ms) else None


def release(name, token):
    return RELEASE(keys=[name], args=[token])


def buy():
    """재고 1 차감. 락 없이 get → set 하면 동시 요청이 같은 값을 읽는다."""
    with r.lock("ex10:lock:stock", timeout=5, blocking_timeout=3):
        stock = int(r.get("ex10:stock"))
        time.sleep(0.01)
        r.set("ex10:stock", stock - 1)


db = FakeDB({1: {"name": "keyboard"}}, delay=0.2)


def get_product(id, use_lock):
    key = f"ex10:product:{id}"
    if (cached := r.get(key)) is not None:
        return json.loads(cached)
    if not use_lock:
        product = db.get(id)
    else:
        with r.lock(f"ex10:lock:product:{id}", timeout=5, blocking_timeout=3):
            # 기다리는 동안 다른 요청이 채웠을 수 있으니 락을 잡은 뒤 다시 확인 (double-check)
            if (cached := r.get(key)) is not None:
                return json.loads(cached)
            product = db.get(id)
    r.set(key, json.dumps(product), ex=60)
    return product


def main():
    reset(r, "ex10")

    # 1. 획득 - SET NX: 키가 없을 때만 성공, EX/PX: 락을 쥔 채 죽어도 풀리게
    token = acquire("ex10:lock:a", 10_000)
    print(token is not None, acquire("ex10:lock:a", 10_000))  # True None

    # 2. 해제 - 토큰이 다르면 지우지 않는다
    print(release("ex10:lock:a", "other-token"), release("ex10:lock:a", token))  # 0 1

    # 3. 그냥 delete로 해제할 때의 문제
    token_a = acquire("ex10:lock:b", 100)
    time.sleep(0.15)                     # A 작업이 길어져 락 만료
    token_b = acquire("ex10:lock:b", 10_000)
    print(release("ex10:lock:b", token_a), r.get("ex10:lock:b") == token_b)  # 0 True
    # 주의: 여기서 r.delete()를 썼다면 A가 B의 락을 지운다. 해제는 반드시 토큰 확인

    # 4. redis-py Lock - 위 토큰/Lua 처리를 대신해 준다. 10명이 동시에 구매
    r.set("ex10:stock", 100)
    with ThreadPoolExecutor(10) as ex:
        for _ in range(10):
            ex.submit(buy)
    print(r.get("ex10:stock"))  # 90

    # 5. 획득 대기 시간 초과 - acquire()는 False, with 문은 LockError
    held = r.lock("ex10:lock:stock", timeout=5)
    held.acquire()
    print(r.lock("ex10:lock:stock", blocking_timeout=0.1).acquire())  # False
    try:
        with r.lock("ex10:lock:stock", blocking_timeout=0.1):
            pass
    except redis.exceptions.LockError as e:
        print(e)  # Unable to acquire lock within the time specified
    held.release()

    # 6. 캐시 스탬피드 - 캐시가 비었을 때 동시 요청이 전부 DB로 몰린다
    # 락을 걸어서 db에 부하가 가지 않게 한다.
    for use_lock in (False, True):
        r.delete("ex10:product:1")
        db.log.clear()
        with ThreadPoolExecutor(10) as ex:
            list(ex.map(lambda _: get_product(1, use_lock), range(10)))
        print(use_lock, db.calls)  # False 10 / True 1

    # 정리하려면 아래 활성화
    # reset(r, "ex10")


if __name__ == "__main__":
    main()

# 확인:
# - docker exec -it my-redis redis-cli GET ex10:stock
# - docker exec -it my-redis redis-cli --scan --pattern 'ex10:lock:*'   (해제 후에는 비어 있음)
