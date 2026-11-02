"""ex5: Hash - 필드 단위 저장/조회/증가, 저장 가능한 값 타입, 필드 TTL."""
import json

import redis

from common import connect, reset


def main():
    r = connect()
    reset(r, "ex5")
    key = "ex5:user:1"

    # 1. 저장 - mapping으로 여러 필드. 반환값은 새로 생긴 필드 개수
    print(r.hset(key, mapping={"name": "kim", "age": 30}))  # 2
    print(r.hset(key, "age", 31))                          # 0 (기존 필드 수정)

    # 2. 조회 - 값은 모두 문자열, 없는 키의 hgetall은 {}
    print(r.hget(key, "age"), r.hmget(key, ["name", "nope"]))  # 31 ['kim', None]
    print(r.hgetall(key), r.hgetall("ex5:nope"))               # {'name': 'kim', 'age': '31'} {}

    # 3. 필드 증가/삭제/존재
    print(r.hincrby(key, "age", 1))                       # 32
    print(r.hdel(key, "age"), r.hexists(key, "age"))      # 1 False

    # 4. 저장 가능한 값 - str/int/float/bytes만
    try:
        r.hset(key, "tags", ["a", "b"])
    except redis.DataError as e:
        print(e)  # Invalid input of type: 'list'. ...
    r.hset(key, "tags", json.dumps(["a", "b"]))
    print(json.loads(r.hget(key, "tags")))  # ['a', 'b']
    # 주의: dict/list/bool/None은 DataError. 직렬화하거나 str로 변환해서 저장

    # 5. TTL - expire는 키 전체, hexpire는 필드 하나 (Redis 7.4+)
    r.hset(key, "token", "abc")
    print(r.hexpire(key, 60, "token"), r.httl(key, "token", "name"))  # [1] [60, -1]

    # 정리하려면 아래 활성화
    # reset(r, "ex5")


if __name__ == "__main__":
    main()

# 확인:
# - docker exec -it my-redis redis-cli HGETALL ex5:user:1
# - docker exec -it my-redis redis-cli HTTL ex5:user:1 FIELDS 1 token
