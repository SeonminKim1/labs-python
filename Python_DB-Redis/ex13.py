"""ex13: [패턴 6] 분산 세션 - Hash에 세션 저장, 요청마다 TTL 연장(sliding expiration)."""
import secrets

from common import connect, reset

r = connect()
TTL = 1800  # 30분 동안 요청이 없으면 만료


def login(user_id, name):
    sid = secrets.token_urlsafe(16)
    with r.pipeline() as pipe:
        pipe.hset(f"ex13:session:{sid}", mapping={"user_id": user_id, "name": name, "cart": 0})
        pipe.expire(f"ex13:session:{sid}", TTL)
        pipe.execute()
    return sid


def load(sid, conn=r):
    """요청마다 호출 - 세션을 읽고 만료 시간을 다시 TTL로 늘린다."""
    with conn.pipeline() as pipe:
        pipe.hgetall(f"ex13:session:{sid}")
        pipe.expire(f"ex13:session:{sid}", TTL)
        session, _ = pipe.execute()
    # 주의: 없는 세션도 hgetall은 None이 아니라 {}를 반환한다
    return session or None


def main():
    reset(r, "ex13")

    # 1. 로그인 - 서버 A가 세션 생성
    sid = login(42, "kim")

    # 2. 다른 서버에서 조회 - Redis만 같으면 어느 서버든 같은 세션
    server_b = connect()
    print(load(sid, server_b))  # {'user_id': '42', 'name': 'kim', 'cart': '0'}

    # 3. 요청이 오면 만료 시간이 다시 30분으로
    r.expire(f"ex13:session:{sid}", 10)  # 만료 직전 상황
    load(sid)
    print(r.ttl(f"ex13:session:{sid}"))  # 1800

    # 4. 필드 단위 수정 - 세션 전체를 읽고 쓰지 않아도 된다
    r.hincrby(f"ex13:session:{sid}", "cart", 1)
    print(r.hget(f"ex13:session:{sid}", "cart"))  # 1

    # 5. 로그아웃 - 키 삭제
    r.delete(f"ex13:session:{sid}")
    print(load(sid))  # None

    # 정리하려면 아래 활성화
    # reset(r, "ex13")


if __name__ == "__main__":
    main()

# 확인:
# - docker exec -it my-redis redis-cli --scan --pattern 'ex13:session:*'
# - docker exec -it my-redis redis-cli HGETALL ex13:session:<sid>
