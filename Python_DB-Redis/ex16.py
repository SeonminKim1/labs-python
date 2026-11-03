"""ex16: Pub/Sub - 채널 구독/발행, 패턴 구독, 구독자 없으면 유실, 콜백 + 백그라운드 스레드."""
import time

from common import connect


def main():
    r = connect()
    # 채널은 키가 아니라서 reset할 게 없다 (KEYS/SCAN에 안 보임)

    # 1. 구독 - pubsub()은 전용 연결을 따로 잡는다
    p = r.pubsub()
    p.subscribe("ex16:news")
    print(p.get_message(timeout=1))
    # {'type': 'subscribe', 'pattern': None, 'channel': 'ex16:news', 'data': 1}
    # 주의: 첫 메시지는 구독 확인(data=구독 채널 수). ignore_subscribe_messages=True면 건너뛴다

    # 2. 발행 - 반환값은 메시지를 받은 구독자 수
    print(r.publish("ex16:news", "hello"))  # 1
    print(p.get_message(timeout=1))
    # {'type': 'message', 'pattern': None, 'channel': 'ex16:news', 'data': 'hello'}
    print(r.pubsub_numsub("ex16:news"))  # [('ex16:news', 1)]

    # 3. 구독자 없으면 유실 - 저장하지 않고 그 순간 연결된 구독자에게만 전달
    print(r.publish("ex16:nobody", "lost"))  # 0
    late = r.pubsub(ignore_subscribe_messages=True)
    late.subscribe("ex16:nobody")
    print(late.get_message(timeout=1))  # None - 구독 전 메시지는 못 받는다
    late.close()
    # 주의: 구독자가 잠깐 끊겨도 그동안 메시지는 사라진다. 꼭 받아야 하면 Streams(xadd/xreadgroup)

    # 4. 패턴 구독 - psubscribe, 받은 메시지에 pattern이 채워진다
    pp = r.pubsub(ignore_subscribe_messages=True)
    pp.psubscribe("ex16:order:*")
    pp.get_message(timeout=1)  # 구독 확인 메시지를 소비 (ignore여도 한 번 호출 필요)
    r.publish("ex16:order:paid", "order-1")
    msg = pp.get_message(timeout=1)
    print(msg["type"], msg["pattern"], msg["channel"], msg["data"])
    # pmessage ex16:order:* ex16:order:paid order-1
    pp.close()

    # 5. 콜백 + 백그라운드 스레드 - 채널별 핸들러를 걸고 run_in_thread로 받는다
    received = []
    cp = r.pubsub(ignore_subscribe_messages=True)
    cp.subscribe(**{"ex16:chat": lambda m: received.append(m["data"])})
    t = cp.run_in_thread(sleep_time=0.01, daemon=True)
    time.sleep(0.1)  # 구독이 끝나기 전에 publish하면 유실되므로 잠깐 대기
    for text in ("hi", "bye"):
        r.publish("ex16:chat", text)
    time.sleep(0.1)
    t.stop()
    print(received)  # ['hi', 'bye']

    # 6. 정리 - 구독 해제 후 연결 반환
    # 주의: 구독 중인 연결은 일반 명령을 못 쓴다. 그래서 pubsub()이 별도 연결을 잡는다
    p.unsubscribe()
    p.close()


if __name__ == "__main__":
    main()

# 확인:
# - docker exec -it my-redis redis-cli SUBSCRIBE ex16:news   (구독 터미널)
# - docker exec -it my-redis redis-cli PUBLISH ex16:news hi  (다른 터미널에서 발행)
# - docker exec -it my-redis redis-cli PUBSUB CHANNELS 'ex16:*'
