"""ex11: [패턴 4] API Rate Limit - 고정 윈도우(INCR + EXPIRE), 슬라이딩 윈도우(Sorted Set)."""
import time
import uuid

from common import connect, reset

r = connect()


def fixed_window(user, limit, window):
    """window초 단위 구간마다 카운터 하나. 초과하면 False (HTTP 429)."""
    key = f"ex11:fixed:{user}:{int(time.time() // window)}"
    with r.pipeline() as pipe:
        pipe.incr(key)
        pipe.expire(key, window, nx=True)  # 구간이 끝나면 키도 사라지게
        count, _ = pipe.execute()
    return count <= limit


def sliding_window(user, limit, window):
    """최근 window초 안의 요청 시각을 Sorted Set(점수=시각)에 담아 센다."""
    key = f"ex11:sliding:{user}"
    now = time.time()
    with r.pipeline() as pipe:
        pipe.zremrangebyscore(key, 0, now - window)  # 창 밖의 오래된 요청 제거
        pipe.zadd(key, {f"{now}:{uuid.uuid4().hex[:6]}": now})
        pipe.zcard(key)
        pipe.expire(key, window)
        count = pipe.execute()[2]
    return count <= limit


def main():
    reset(r, "ex11")

    # 1. 고정 윈도우 - 3회 제한
    print([fixed_window("kim", 3, 60) for _ in range(5)])  # [True, True, True, False, False]
    # 주의: 구간 경계에 몰리면 (앞 구간 끝 3회 + 다음 구간 시작 3회) 짧은 시간에 한도의 2배가 통과한다

    # 2. 슬라이딩 윈도우 - 최근 1초 3회 제한, 시간이 지나면 다시 허용
    print([sliding_window("kim", 3, 1) for _ in range(5)])  # [True, True, True, False, False]
    time.sleep(1.1)
    print(sliding_window("kim", 3, 1))  # True
    # 주의: 멤버가 같으면 덮어써서 개수가 줄어든다. 같은 시각 요청 대비로 고유값을 붙인다
    # 거절된 요청도 기록되어 한도에 포함된다 (계속 두드리면 계속 막힘)

    # 정리하려면 아래 활성화
    # reset(r, "ex11")


if __name__ == "__main__":
    main()

# 확인:
# - docker exec -it my-redis redis-cli --scan --pattern 'ex11:*'
# - docker exec -it my-redis redis-cli ZRANGE ex11:sliding:kim 0 -1 WITHSCORES
