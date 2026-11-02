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

- `common.py`: 연결 `connect()`, 예제 키 초기화 `reset(r, prefix)`, 키 상태 확인 `show(r, key)`, 패턴 예제용 가짜 DB `FakeDB`(호출 횟수 `calls`)
- 키 이름: `ex<번호>:<이름>`. 각 예제는 시작할 때 자기 키를 지우므로 재실행해도 결과가 같다
- 확인: `docker exec -it my-redis redis-cli ...`

## 목차

| # | 파일 | 내용 |
|---|------|------|
| 1 | `ex1.py` | 연결(`decode_responses`) + String (`set`/`get`, `nx`/`get=True`, `incr`, `mset`/`mget`, `getdel`) |
| 2 | `ex2.py` | 키 관리·TTL (`ex`, `ttl` -1/-2, `expire(nx=)`, `persist`, `keepttl`, `exists`, `scan_iter` vs `keys`, `unlink`) |
| 3 | `ex3.py` | List (`lpush`/`rpush`, `lrange`, `lpop`/`rpop`, `lrem`, `ltrim`, `blpop` 큐) |
| 4 | `ex4.py` | Set (`sadd` 반환값, `smembers`/`sismember`/`smismember`, `srem`, `sinter`/`sunion`/`sdiff`) |
| 5 | `ex5.py` | Hash (`hset(mapping=)`, `hget`/`hmget`/`hgetall`, `hincrby`, `hdel`, 값 타입 제한, 필드 TTL `hexpire`) |
| 6 | `ex6.py` | Sorted Set (`zadd`, `zincrby`, `zrange(desc/byscore)`, `zrevrank`, `zcount`, `zremrangebyscore`, 동점 정렬) |
| 7 | `ex7.py` | 파이프라인·트랜잭션 (`pipeline`, MULTI/EXEC 롤백 없음, `watch` + `WatchError`, `transaction()`) |
| 8 | `ex8.py` | [패턴 1] 캐싱: Cache-Aside(조회 시 채움, 수정 시 삭제), Write-Through, TTL 지터 |
| 9 | `ex9.py` | [패턴 2] 인증번호: TTL 만료, 성공 시 삭제(1회용), 실패 횟수 제한 |
| 10 | `ex10.py` | [패턴 3] 분산 락: `SET NX PX`, 토큰 확인 해제(Lua `register_script`), `r.lock`, 캐시 스탬피드 + double-check |
| 11 | `ex11.py` | [패턴 4] Rate Limit: 고정 윈도우(`incr` + `expire(nx=)`), 슬라이딩 윈도우(Sorted Set) |
| 12 | `ex12.py` | [패턴 5] 최근 본 상품: `lrem` → `lpush` → `ltrim` + `expire`를 파이프라인으로 |
| 13 | `ex13.py` | [패턴 6] 분산 세션: Hash 세션, 요청마다 TTL 연장(sliding expiration), 필드 단위 수정 |
| 14 | `ex14.py` | [패턴 7] 조회수·좋아요: `set(nx, ex)` 중복 조회 제거, `sadd` 좋아요 판정, `getdel` write-back |
| 15 | `ex15.py` | [패턴 8] 실시간 랭킹: `zincrby`, 일별 키 + `zunionstore` 주간 합산, 동점 시 먼저 달성 우선, DB로 복구 |

제외: Pub/Sub, Streams, Cluster/Sentinel, Redis Stack 모듈(JSON, Search)
