# example-pymongo

pymongo 학습용 예제 모음. 작성 규칙은 `EXAMPLE_GUIDE.md` 참고.

## 사전 준비

- Python >= 3.11, [uv](https://docs.astral.sh/uv/)
- `mongodb://localhost:27017`에서 접속 가능한 MongoDB
  (예: `docker run -d -p 27017:27017 mongo`)
- 의존성 설치: `uv sync`

## 실행

```
uv run python ex1.py
```

공용 연결 설정(`MONGO_URI`, `DB_NAME`)은 `common.py`에 있다.

## 목차

비슷한 유형끼리 묶어서 번호를 배치했다: 연결 → 기본 CRUD → 조회 기법 → 쓰기 기법 →
인덱스 → 집계.

| # | 파일 | 내용 |
|---|------|------|
| 1 | `ex1.py` | 서버 연결 확인 (`ping`, 버전, DB 목록) |
| 2 | `ex2.py` | 문서 삽입 (`insert_one`, `insert_many`) |
| 3 | `ex3.py` | 문서 조회 (`find_one`, `find`, 필터 · 정렬 · projection) |
| 4 | `ex4.py` | 문서 수정 — 업데이트 연산자 모음 (`$set`, `$inc`, upsert, `$mul`, `$max`, `$min`, `$push`, `$addToSet`, `$unset`, `$rename`) |
| 5 | `ex5.py` | 문서 삭제 (`delete_one`, `delete_many`) |
| 6 | `ex6.py` | 정렬/페이지네이션 (`sort`, `skip`/`limit` vs 대규모용 keyset 페이지네이션) |
| 7 | `ex7.py` | 배열/중첩 문서 조회 (dot notation, `$in`, `$all`, `$elemMatch`) |
| 8 | `ex8.py` | 필드의 고유 값 목록 조회 (`distinct`) |
| 9 | `ex9.py` | datetime 저장과 범위 조회 |
| 10 | `ex10.py` | 텍스트 인덱스 기반 전문 검색 (`$text`, `$search`, textScore 정렬) |
| 11 | `ex11.py` | 원자적 조회+수정/삭제 (`find_one_and_update`, `find_one_and_delete`, 카운터/작업 큐 claim 패턴) |
| 12 | `ex12.py` | 여러 연산 한 번에 실행 (`bulk_write`) |
| 13 | `ex13.py` | 인덱스 (`create_index`, `list_indexes`, `explain`) |
| 14 | `ex14.py` | 고유 인덱스 + 중복 키 에러 처리 (`unique=True`, `DuplicateKeyError`) |
| 15 | `ex15.py` | 집계 파이프라인 (`aggregate`, `$match`, `$group`, `$sort`) |
| 16 | `ex16.py` | 집계로 컬렉션 조인 (`$lookup`, `$unwind`, `$project`) |

(예제를 추가/수정할 때마다 이 표도 같이 갱신한다. 꼭 필요하고 많이 쓰이는 것 위주로
16개에서 마무리 — 20개는 상한선일 뿐 목표가 아니다. 너무 세부적인 문법/설정 위주
항목은 의도적으로 뺐다.)
