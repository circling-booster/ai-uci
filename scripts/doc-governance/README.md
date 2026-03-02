# docs/doc-governance

이 디렉터리는 `docs/decisions` 및 `docs/reports`의 문서 거버넌스 도구를 포함한다.

## 사용 방법

```bash
python scripts/doc-governance/validate.py --check
python scripts/doc-governance/validate.py --generate-index
python scripts/doc-governance/validate.py --check --generate-index --summary
```

## 설명

- `--check`
  - ADR/Report의 front matter 필수 필드를 검사한다.
  - 상태/도메인/유형/기간 형식을 검사한다.
  - 경로 규칙, ID 형식, 교차 참조(`ADR-*`, `RPT-*`)를 검사한다.
- `--generate-index`
  - `--check` 통과 시 인덱스를 재생성한다.
  - 출력 파일:
    - `docs/decisions/registry/decisions-index.md`
    - `docs/reports/registry/reports-index.md`
- `--summary`
  - 검증 건수(에러/경고)와 집계 통계를 추가 출력한다.

## 의존성

- Python 3.8+ (표준 라이브러리만 사용)
- 추가 패키지 설치 불필요
