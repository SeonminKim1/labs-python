"""ex3: List - 양끝 삽입/꺼내기, 범위 조회, 값 삭제, 최신 N개 유지, 블로킹 큐."""
from common import connect, reset


def main():
    r = connect()
    reset(r, "ex3")
    key = "ex3:items"

    # 1. 삽입 - rpush는 뒤, lpush는 앞. 반환값은 삽입 후 길이
    r.rpush(key, "a", "b", "c")
    print(r.lpush(key, "x", "y"))  # 5
    # 주의: lpush는 인자 역순으로 앞에 쌓인다 (y가 맨 앞)

    # 2. 조회 - 0, -1은 전체, 음수는 뒤에서부터
    print(r.lrange(key, 0, -1), r.lindex(key, -1))  # ['y', 'x', 'a', 'b', 'c'] c

    # 3. 꺼내기 - 꺼내면서 삭제, count를 주면 리스트
    print(r.lpop(key), r.rpop(key), r.lpop(key, 2))  # y c ['x', 'a']

    # 4. 값으로 삭제 - count=0은 전부, 반환값은 삭제 개수
    r.rpush(key, "a", "c", "a")
    print(r.lrem(key, 0, "a"), r.lrange(key, 0, -1))  # 2 ['b', 'c']

    # 5. 최신 N개만 유지 - lpush 후 ltrim(0, N-1)
    r.lpush(key, "d", "e", "f")
    r.ltrim(key, 0, 2)
    print(r.lrange(key, 0, -1))  # ['f', 'e', 'd']

    # 6. 블로킹 큐 - 비어 있으면 timeout(초)까지 대기
    r.rpush("ex3:queue", "job1")
    print(r.blpop("ex3:queue", timeout=1))  # ('ex3:queue', 'job1')
    print(r.blpop("ex3:queue", timeout=1))  # None

    # 7. 빈 리스트
    print(r.exists("ex3:queue"))  # 0
    # 주의: 원소가 0개가 되면 키 자체가 사라진다

    # 정리하려면 아래 활성화
    # reset(r, "ex3")


if __name__ == "__main__":
    main()

# 확인:
# - docker exec -it my-redis redis-cli LRANGE ex3:items 0 -1
# - docker exec -it my-redis redis-cli BLPOP ex3:queue 5   (다른 터미널에서 RPUSH ex3:queue job)
