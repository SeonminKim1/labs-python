"""ex8: [패턴 1] 캐싱 - Cache-Aside(조회 시 채우고 수정 시 삭제), Write-Through(수정 시 갱신), TTL 지터."""
import json
import random

from common import FakeDB, connect, reset

r = connect()
db = FakeDB({1: {"name": "keyboard", "price": 50000}})
TTL = 300


def cache_key(id):
    return f"ex8:product:{id}"


def get_product(id):
    """Cache-Aside: 캐시 → 없으면 DB → 캐시에 저장."""
    if (cached := r.get(cache_key(id))) is not None:
        return json.loads(cached)
    product = db.get(id)
    # TTL에 무작위 지터를 더해 같은 시각에 들어간 키들이 동시에 만료되지 않게 한다
    r.set(cache_key(id), json.dumps(product), ex=TTL + random.randint(0, 60))
    return product


def update_price_cache_aside(id, price):
    db.update(id, price=price)
    r.delete(cache_key(id))  # 다음 조회 때 DB에서 다시 채운다


def update_price_write_through(id, price):
    db.update(id, price=price)
    r.set(cache_key(id), json.dumps(db.data[id]), ex=TTL + random.randint(0, 60))


def main():
    reset(r, "ex8")

    # 1. 첫 조회는 DB, 이후는 캐시
    get_product(1)
    get_product(1)
    print(db.calls, r.ttl(cache_key(1)))  # 1 300~360

    # 2. 캐시 무효화 누락
    db.update(1, price=45000)
    print(get_product(1)["price"])  # 50000
    # 주의: DB만 고치면 TTL이 끝날 때까지 옛 값이 나간다. TTL은 이런 실수의 안전망

    # 3. Cache-Aside 수정 - DB 수정 후 캐시 삭제 → 다음 조회에서 DB
    update_price_cache_aside(1, 40000)
    print(get_product(1)["price"], db.calls)  # 40000 2

    # 4. Write-Through 수정 - 캐시를 새 값으로 덮어써서 다음 조회도 캐시 적중
    update_price_write_through(1, 35000)
    print(get_product(1)["price"], db.calls)  # 35000 2

    # 정리하려면 아래 활성화
    # reset(r, "ex8")


if __name__ == "__main__":
    main()

# 확인:
# - docker exec -it my-redis redis-cli GET ex8:product:1
# - docker exec -it my-redis redis-cli TTL ex8:product:1
