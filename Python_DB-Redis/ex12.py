"""ex12: [패턴 5] 최근 본 상품 - List로 중복 없이 최신 N개 유지."""
from common import connect, reset

r = connect()
MAX_ITEMS = 3
TTL = 30 * 24 * 3600  # 30일 동안 안 들어오면 정리


def view(user, product_id):
    key = f"ex12:recent:{user}"
    with r.pipeline() as pipe:  # 네 명령을 한 번에, 중간 상태가 보이지 않게
        pipe.lrem(key, 0, product_id)  # 이미 있으면 빼고
        pipe.lpush(key, product_id)    # 맨 앞에 넣고
        pipe.ltrim(key, 0, MAX_ITEMS - 1)
        pipe.expire(key, TTL)
        pipe.execute()


def recent(user):
    return r.lrange(f"ex12:recent:{user}", 0, -1)


def main():
    reset(r, "ex12")

    # 1. 조회한 순서의 역순(최신이 앞)
    for pid in (101, 102, 103):
        view("kim", pid)
    print(recent("kim"))  # ['103', '102', '101']

    # 2. 다시 본 상품은 맨 앞으로 이동
    view("kim", 101)
    print(recent("kim"))  # ['101', '103', '102']
    # 주의: lrem 없이 lpush만 하면 같은 상품이 여러 번 쌓인다

    # 3. N개를 넘으면 가장 오래된 것부터 잘림
    view("kim", 104)
    print(recent("kim"), r.ttl("ex12:recent:kim"))  # ['104', '101', '103'] 2592000

    # 정리하려면 아래 활성화
    # reset(r, "ex12")


if __name__ == "__main__":
    main()

# 확인:
# - docker exec -it my-redis redis-cli LRANGE ex12:recent:kim 0 -1
