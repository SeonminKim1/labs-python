# example-beanie

[Beanie](https://beanie-odm.dev/) (MongoDB 비동기 ODM) 학습용 예제 모음.
pymongo 예제(`../Python_DB_Pymongo_Async`)와 같은 형식이며, 모델(pydantic) 기반으로 같은 일을 어떻게 하는지 비교하며 보면 좋다.

## 사전 준비

- Python >= 3.11, [uv](https://docs.astral.sh/uv/)
- `mongodb://localhost:27017`에서 접속 가능한 MongoDB
  (예: `docker run -d -p 27017:27017 mongo`)
- 의존성 설치: `uv sync` (beanie 2.x — motor가 아닌 pymongo `AsyncMongoClient` 기반)

## 실행

```
uv run python ex1.py
```

공용 연결/초기화(`MONGO_URI`, `DB_NAME`, `init(*models)`)는 `common.py`에 있다.
각 예제는 `ex<번호>_<이름>` 컬렉션을 사용한다.

## 목차

연결 → 기본 CRUD → 조회 기법 → 쓰기 기법 → 인덱스 → 관계/집계 순으로 배치했다.

| # | 파일 | 내용 |
|---|------|------|
| 1 | `ex1.py` | `Document` 정의 + `init_beanie` 연결, 저장된 raw 문서 모양 확인 |
| 2 | `ex2.py` | 삽입 (`insert`, `insert_many`, `save`) + pydantic 검증 함정과 `validate_on_save` |
| 3 | `ex3.py` | 조회 (`get`, `find_one`, `find`, 필드 비교식, `beanie.operators`, dict 필터) |

(예제를 추가/수정할 때마다 이 표도 같이 갱신한다.)
