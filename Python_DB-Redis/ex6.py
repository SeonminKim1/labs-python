"""ex6: Sorted Set - 점수로 정렬된 집합, 점수 증가, 순위/범위 조회."""
from common import connect, reset


def main():
    r = connect()
    reset(r, "ex6")
    key = "ex6:scores"

    # 1. 추가 - 반환값은 새 멤버 개수. 기존 멤버는 점수만 갱신
    print(r.zadd(key, {"kim": 10, "lee": 20, "park": 15}))  # 3
    print(r.zadd(key, {"kim": 12}))                         # 0

    # 2. 점수 증가 - 없는 멤버는 0에서 시작, 새 점수(float) 반환
    print(r.zincrby(key, 5, "kim"), r.zincrby(key, 3, "choi"))  # 17.0 3.0

    # 3. 정렬 조회 - 기본 오름차순, desc=True로 내림차순
    print(r.zrange(key, 0, -1))                               # ['choi', 'park', 'kim', 'lee']
    print(r.zrange(key, 0, 1, desc=True, withscores=True))    # [('lee', 20.0), ('kim', 17.0)]

    # 4. 순위/점수 - 순위는 0부터, 없는 멤버는 None
    print(r.zrevrank(key, "kim"), r.zscore(key, "kim"), r.zscore(key, "nope"))  # 1 17.0 None

    # 5. 점수 범위 - byscore=True, 개수는 zcount ("-inf", "+inf" 사용 가능)
    print(r.zrange(key, 10, 17, byscore=True), r.zcount(key, 10, "+inf"))  # ['park', 'kim'] 3

    # 6. 삭제 - 멤버 지정 또는 점수 범위
    print(r.zremrangebyscore(key, "-inf", 5), r.zrem(key, "park"))  # 1 1

    # 7. 동점 정렬
    r.zadd(key, {"ahn": 20})
    print(r.zrange(key, 0, -1, desc=True, withscores=True))  # [('lee', 20.0), ('ahn', 20.0), ('kim', 17.0)]
    # 주의: 동점이면 멤버 사전순 (desc면 역순). 먼저 달성한 쪽을 앞에 두려면 점수에 시간을 섞는다 (ex15)

    # 정리하려면 아래 활성화
    # reset(r, "ex6")


if __name__ == "__main__":
    main()

# 확인:
# - docker exec -it my-redis redis-cli ZRANGE ex6:scores 0 -1 REV WITHSCORES
