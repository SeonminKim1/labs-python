"""ex15: [패턴 8] 실시간 랭킹 - Sorted Set으로 점수 누적, 일별 키, 주간 합산, 동점 처리."""
from common import connect, reset

r = connect()


def add_score(day, user, points):
    key = f"ex15:rank:{day}"
    r.zincrby(key, points, user)
    r.expire(key, 8 * 24 * 3600)  # 주간 합산이 끝나면 자동 정리


def top(key, n):
    return r.zrange(key, 0, n - 1, desc=True, withscores=True)


def main():
    reset(r, "ex15")

    # 1. 점수 누적 - 정렬은 Redis가 유지, 조회는 상위 N개만
    add_score("20261101", "kim", 50)
    add_score("20261101", "lee", 70)
    add_score("20261101", "kim", 30)
    print(top("ex15:rank:20261101", 2))  # [('kim', 80.0), ('lee', 70.0)]

    # 2. 내 순위 - zrevrank는 0부터
    print(r.zrevrank("ex15:rank:20261101", "lee") + 1, r.zscore("ex15:rank:20261101", "lee"))  # 2 70.0

    # 3. 주간 랭킹 - 일별 키를 합산해 새 키에 저장, 반환값은 멤버 수
    add_score("20261102", "lee", 40)
    add_score("20261102", "park", 60)
    print(r.zunionstore("ex15:rank:week", ["ex15:rank:20261101", "ex15:rank:20261102"]))  # 3
    print(top("ex15:rank:week", 3))  # [('lee', 110.0), ('kim', 80.0), ('park', 60.0)]

    # 4. 동점이면 먼저 달성한 사람이 위로 - 점수 * 10^10 + (큰 수 - 달성 시각)
    def tie_score(points, ts):
        return points * 10**10 + (10**10 - 1 - ts)

    r.zadd("ex15:plain", {"ahn": 100, "yoon": 100})
    print(r.zrange("ex15:plain", 0, -1, desc=True))  # ['yoon', 'ahn']
    r.zadd("ex15:best", {"yoon": tie_score(100, 1_700_000_200)})  # 늦게 달성
    r.zadd("ex15:best", {"ahn": tie_score(100, 1_700_000_100)})   # 먼저 달성
    print([(u, int(s // 10**10)) for u, s in top("ex15:best", 2)])  # [('ahn', 100), ('yoon', 100)]
    # 주의: 그냥 동점이면 달성 순서와 무관하게 멤버 이름 역사전순(desc)
    # 점수는 double이라 points가 약 90만을 넘으면 하위 자리(시각)가 뭉개진다

    # 5. 복구 - Redis 데이터가 사라지면 DB 기록으로 다시 채운다
    r.delete("ex15:rank:20261101")
    db_rows = [("kim", 80), ("lee", 70)]
    r.zadd("ex15:rank:20261101", dict(db_rows))
    print(top("ex15:rank:20261101", 2))  # [('kim', 80.0), ('lee', 70.0)]

    # 정리하려면 아래 활성화
    # reset(r, "ex15")


if __name__ == "__main__":
    main()

# 확인:
# - docker exec -it my-redis redis-cli ZRANGE ex15:rank:week 0 -1 REV WITHSCORES
