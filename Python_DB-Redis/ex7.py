"""ex7: 파이프라인과 트랜잭션 - 명령 묶어 보내기, MULTI/EXEC, WATCH 낙관적 락."""
import redis

from common import connect, reset


def main():
    r = connect()
    reset(r, "ex7")

    # 1. 파이프라인 - 명령을 모아 한 번의 왕복으로 보내고, 결과는 execute()의 리스트
    with r.pipeline() as pipe:
        pipe.set("ex7:count", 1)
        pipe.incr("ex7:count")
        print(type(pipe.get("ex7:count")).__name__)  # Pipeline
        print(pipe.execute())                        # [True, 2, '2']
    # 주의: execute() 전에는 값이 아니라 파이프라인 객체가 반환된다

    # 2. 트랜잭션 - pipeline()은 기본 transaction=True(MULTI/EXEC)라 중간에 다른 명령이 끼어들지 않는다
    #    transaction=False는 왕복만 줄이고 원자성은 없다
    with r.pipeline() as pipe:
        pipe.incr("ex7:count")
        pipe.lpush("ex7:count", "x")  # 문자열 키에 리스트 명령 → 실패
        pipe.incr("ex7:count")
        print(pipe.execute(raise_on_error=False))  # [3, ResponseError(WRONGTYPE ...), 4]
    # 주의: 롤백이 없다. 실패한 명령만 빠지고 나머지는 실행된다

    # 3. WATCH - 감시한 키가 EXEC 전에 바뀌면 WatchError로 전체 취소 (낙관적 락)
    r.set("ex7:stock", 10)
    with r.pipeline() as pipe:
        pipe.watch("ex7:stock")
        stock = int(pipe.get("ex7:stock"))  # watch 후에는 즉시 실행
        r.set("ex7:stock", 5)               # 다른 클라이언트가 끼어든 상황
        pipe.multi()                        # 대기열에 담아주세요~ 역할
        pipe.set("ex7:stock", stock - 1)
        try:
            pipe.execute()
        except redis.WatchError:
            print("WatchError", r.get("ex7:stock"))  # WatchError 5

    # 4. transaction() - WATCH + 재시도 루프를 대신해 준다
    def decrease(pipe):
        stock = int(pipe.get("ex7:stock"))
        pipe.multi()
        pipe.set("ex7:stock", stock - 1)

    print(r.transaction(decrease, "ex7:stock"), r.get("ex7:stock"))  # [True] 4

    # 정리하려면 아래 활성화
    # reset(r, "ex7")


if __name__ == "__main__":
    main()

# 확인:
# - docker exec -it my-redis redis-cli MGET ex7:count ex7:stock
