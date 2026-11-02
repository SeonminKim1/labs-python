"""ex1: 연결과 String - 저장/조회, 조건부 저장, 원자적 카운터, 여러 키 한 번에."""
import redis

from common import connect, reset


def main():
    r = connect()
    reset(r, "ex1")

    # 1. decode_responses
    r.set("ex1:greeting", "hello")
    print(connect(decode=False).get("ex1:greeting"), r.get("ex1:greeting"))  # b'hello' hello
    # 주의: 기본값은 bytes 반환이라 b"hello" == "hello"가 False

    # 2. set/get - 숫자도 문자열로 저장, 없는 키는 None
    r.set("ex1:age", 30)
    print(repr(r.get("ex1:age")), r.get("ex1:nope"))  # '30' None

    # 3. 조건부 저장 - nx: 없을 때만, get=True: 이전 값 반환
    print(r.set("ex1:greeting", "hi", nx=True))   # None
    print(r.set("ex1:greeting", "hi", get=True))  # hello
    # 주의: 조건 불충족 시 False가 아니라 None

    # 4. 원자적 카운터 - 없는 키는 0에서 시작
    r.incr("ex1:visits")
    print(r.incrby("ex1:visits", 10))  # 11
    try:
        r.incr("ex1:greeting")
    except redis.ResponseError as e:
        print(e)  # value is not an integer or out of range
    # 주의: python 레벨에서 get → +1 → set으로 직접 세면 동시 요청에서 값이 유실된다 (동시성 에러)

    # 5. mset/mget - 여러 키를 한 번의 왕복으로
    r.mset({"ex1:a": 1, "ex1:b": 2})
    print(r.mget("ex1:a", "ex1:b", "ex1:nope"))  # ['1', '2', None]

    # 6. getdel - 읽고 바로 삭제 (원자적)
    print(r.getdel("ex1:a"), r.get("ex1:a"))  # 1 None

    # 정리하려면 아래 활성화
    # reset(r, "ex1")


if __name__ == "__main__":
    main()

# 확인:
# - docker exec -it my-redis redis-cli --scan --pattern 'ex1:*'
# - docker exec -it my-redis redis-cli MGET ex1:greeting ex1:age ex1:visits
