# example-redis

[redis-py](https://redis.readthedocs.io/) 학습용 예제 모음. 기본 자료형·연산 + 실무 패턴 8개([참고 글](https://yubi5050.tistory.com/426)).

## 사전 준비

- Python >= 3.11, [uv](https://docs.astral.sh/uv/)
- `localhost:6379`에서 접속 가능한 Redis (예제는 Redis 8.x 기준)
  (예: `docker run -d --name my-redis -p 6379:6379 redis`)
- 의존성 설치: `uv sync` (redis-py 8.x)

## 실행

```
uv run python ex1.py
```

- `common.py`: 연결 `connect()`, 예제 키 초기화 `reset(r, prefix)`, 키 상태 확인 `show(r, key)`
- 키 이름: `ex<번호>:<이름>`. 각 예제는 시작할 때 자기 키를 지우므로 재실행해도 결과가 같다
- 확인: `docker exec -it my-redis redis-cli ...`

## 목차

| # | 파일 | 내용 |
|---|------|------|
| 1 | `ex1.py` | 연결(`decode_responses`) + String (`set`/`get`, `nx`/`get=True`, `incr`, `mset`/`mget`, `getdel`) |
| 2 | `ex2.py` | 키 관리·TTL (`ex`, `ttl` -1/-2, `expire(nx=)`, `persist`, `keepttl`, `exists`, `scan_iter` vs `keys`, `unlink`) |
| 3 | `ex3.py` | List (`lpush`/`rpush`, `lrange`, `lpop`/`rpop`, `lrem`, `ltrim`, `blpop` 큐) |
