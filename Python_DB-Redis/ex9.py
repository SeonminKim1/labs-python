"""ex9: [패턴 2] 인증번호 - TTL로 자동 만료, 성공 시 삭제, 실패 횟수 제한."""
import random
import time

from common import connect, reset

r = connect()
TTL = 180
MAX_ATTEMPTS = 5


def send_code(phone, ttl=TTL):
    code = f"{random.randint(0, 999999):06d}"
    r.set(f"ex9:code:{phone}", code, ex=ttl)
    r.delete(f"ex9:attempts:{phone}")  # 재발송하면 실패 횟수 초기화
    return code


def verify(phone, code):
    attempts_key = f"ex9:attempts:{phone}"
    attempts = r.incr(attempts_key)
    r.expire(attempts_key, TTL, nx=True)  # 첫 시도에만 TTL
    if attempts > MAX_ATTEMPTS:
        return "blocked"
    saved = r.get(f"ex9:code:{phone}")
    if saved is None:
        return "expired"
    # delete가 1을 반환한 요청 하나만 성공 → 같은 코드로 동시에 두 번 성공하지 못한다
    if saved == code and r.delete(f"ex9:code:{phone}") == 1:
        r.delete(attempts_key)
        return "ok"
    return "wrong"


def main():
    reset(r, "ex9")
    phone = "01012345678"

    # 1. 발송 - 코드를 TTL과 함께 저장
    code = send_code(phone)
    print(r.ttl(f"ex9:code:{phone}"))  # 180

    # 2. 실패 → 시도 횟수 증가
    print(verify(phone, "000000"), r.get(f"ex9:attempts:{phone}"))  # wrong 1

    # 3. 성공 → 코드 삭제, 같은 코드 재사용 불가
    print(verify(phone, code), verify(phone, code))  # ok expired

    # 4. 실패 횟수 초과 → 맞는 코드여도 차단
    code = send_code(phone)
    for _ in range(MAX_ATTEMPTS):
        verify(phone, "000000")
    print(verify(phone, code))  # blocked
    # 주의: 횟수 제한이 없으면 6자리 코드는 100만 번 안에 반드시 뚫린다

    # 5. 만료 → TTL이 지나면 키가 사라진다
    code = send_code(phone, ttl=1)
    time.sleep(1.1)
    print(verify(phone, code))  # expired

    # 정리하려면 아래 활성화
    # reset(r, "ex9")


if __name__ == "__main__":
    main()

# 확인:
# - docker exec -it my-redis redis-cli --scan --pattern 'ex9:*'
# - docker exec -it my-redis redis-cli TTL ex9:attempts:01012345678
