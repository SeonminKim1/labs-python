"""ex4: Set - 중복 없는 집합, 포함 여부, 집합 연산."""
from common import connect, reset


def main():
    r = connect()
    reset(r, "ex4")

    # 1. 추가 - 반환값은 새로 추가된 개수 (이미 있으면 0)
    print(r.sadd("ex4:likes", "kim", "lee", "kim"))  # 2
    print(r.sadd("ex4:likes", "kim"))                # 0

    # 2. 조회 - smembers는 파이썬 set
    print(sorted(r.smembers("ex4:likes")), r.scard("ex4:likes"))  # ['kim', 'lee'] 2
    print(r.sismember("ex4:likes", "kim"), r.smismember("ex4:likes", ["kim", "park"]))  # 1 [1, 0]
    # 주의: smembers는 순서가 없고 전체를 한 번에 가져온다. 큰 집합은 sscan_iter

    # 3. 삭제 - 반환값은 실제 삭제 개수
    print(r.srem("ex4:likes", "lee", "nope"))  # 1

    # 4. 집합 연산 - 교집합/합집합/차집합
    r.sadd("ex4:a", "kim", "lee", "park")
    r.sadd("ex4:b", "lee", "choi")
    print(sorted(r.sinter("ex4:a", "ex4:b")))  # ['lee']
    print(sorted(r.sunion("ex4:a", "ex4:b")))  # ['choi', 'kim', 'lee', 'park']
    print(sorted(r.sdiff("ex4:a", "ex4:b")))   # ['kim', 'park']

    # 정리하려면 아래 활성화
    # reset(r, "ex4")


if __name__ == "__main__":
    main()

# 확인:
# - docker exec -it my-redis redis-cli SMEMBERS ex4:likes
# - docker exec -it my-redis redis-cli SINTER ex4:a ex4:b
