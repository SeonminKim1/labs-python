"""ex2: 키 관리와 TTL - 만료 설정/확인, TTL이 지워지는 경우, 존재 확인, SCAN, 삭제."""
from common import connect, reset, show


def main():
    r = connect()
    reset(r, "ex2")

    # 1. 저장과 동시에 TTL - ex=초, px=밀리초
    r.set("ex2:code", "123456", ex=180)
    r.set("ex2:forever", "v")
    print(show(r, "ex2:code"))  # ex2:code [string, ttl=180] 123456

    # 2. TTL 반환값 - 남은 초 / -1: 만료 없음 / -2: 키 없음
    print(r.ttl("ex2:code"), r.ttl("ex2:forever"), r.ttl("ex2:nope"))  # 180 -1 -2

    # 3. TTL 붙이기/떼기 - nx=True면 TTL이 없을 때만 설정
    r.expire("ex2:forever", 60)
    r.persist("ex2:forever")
    print(r.expire("ex2:code", 999, nx=True))  # False

    # 4. 덮어쓰기와 TTL
    r.set("ex2:code", "654321")
    print(r.ttl("ex2:code"))  # -1
    r.set("ex2:code", "111111", ex=180)
    r.set("ex2:code", "222222", keepttl=True)
    print(r.ttl("ex2:code"))  # 180
    # 주의: 일반 set은 TTL을 지운다. 유지하려면 keepttl=True (incr은 TTL 유지)

    # 5. 존재/자료형 - exists는 존재하는 키 개수
    print(r.exists("ex2:code", "ex2:nope"), r.type("ex2:nope"))  # 1 none

    # 6. 키 탐색 - 커서 단위로 나눠 조회, 순서 보장 없음
    print(sorted(r.scan_iter("ex2:*")))  # ['ex2:code', 'ex2:forever']
    # 주의: keys()는 전체를 한 번에 훑는 동안 서버를 막는다. 운영에서는 scan_iter

    # 7. 삭제 - 삭제 개수 반환. unlink는 메모리 회수를 백그라운드로
    print(r.unlink("ex2:forever", "ex2:nope"))  # 1

    # 정리하려면 아래 활성화
    # reset(r, "ex2")


if __name__ == "__main__":
    main()

# 확인:
# - docker exec -it my-redis redis-cli --scan --pattern 'ex2:*'
# - docker exec -it my-redis redis-cli TTL ex2:code
