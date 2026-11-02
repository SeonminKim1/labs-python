"""ex14: [패턴 7] 조회수·좋아요 - SET NX로 중복 조회 제거, Set으로 좋아요, 주기적 DB 반영(write-back)."""
from common import FakeDB, connect, reset

r = connect()
db = FakeDB({1: {"views": 1000}})


def view(post, user):
    """같은 사용자는 24시간에 한 번만 센다."""
    if r.set(f"ex14:viewed:{post}:{user}", 1, nx=True, ex=24 * 3600):
        r.incr(f"ex14:views:{post}")  # DB에 아직 반영 안 된 증가분


def like(post, user):
    return r.sadd(f"ex14:likes:{post}", user) == 1  # 1이면 새 좋아요


def flush_views():
    """배치 작업 - 쌓인 증가분을 DB에 더하고 Redis 카운터는 비운다."""
    for key in r.scan_iter("ex14:views:*"):
        post = int(key.rsplit(":", 1)[1])
        if count := r.getdel(key):
            db.data[post]["views"] += int(count)


def main():
    reset(r, "ex14")

    # 1. 조회수 - 같은 사용자 반복 조회는 한 번만
    for user in ("kim", "kim", "kim", "lee"):
        view(1, user)
    print(r.get("ex14:views:1"))  # 2

    # 2. 좋아요 - sadd 반환값으로 새 좋아요 판정, 취소는 srem
    print(like(1, "kim"), like(1, "kim"), like(1, "lee"))  # True False True
    r.srem("ex14:likes:1", "lee")
    print(r.scard("ex14:likes:1"))  # 1

    # 3. write-back - 매 조회마다 DB에 쓰지 않고 모아서 반영
    flush_views()
    print(db.data[1]["views"], r.exists("ex14:views:1"))  # 1002 0
    # 주의: get 후 delete로 나누면 그 사이 들어온 증가분이 사라진다. getdel로 원자적으로
    # Redis가 죽으면 아직 반영 안 된 증가분은 잃는다 (조회수처럼 약간의 유실이 괜찮은 값에만)

    # 정리하려면 아래 활성화
    # reset(r, "ex14")


if __name__ == "__main__":
    main()

# 확인:
# - docker exec -it my-redis redis-cli --scan --pattern 'ex14:*'
# - docker exec -it my-redis redis-cli SMEMBERS ex14:likes:1
