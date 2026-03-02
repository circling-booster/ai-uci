# docs/doc-governance

이 디렉터리는 `docs/decisions` 및 `docs/reports`의 문서 거버넌스 도구를 포함한다.

## 사용 방법

```bash
python scripts/doc-governance/validate.py --check
python scripts/doc-governance/validate.py --generate-index
python scripts/doc-governance/validate.py --check --generate-index --summary
```

### 로컬 Git 훅으로 실시간 검증

`docs/decisions`, `docs/reports` 경로의 파일이 커밋 스테이징될 때마다
자동으로 `--check`를 실행하려면 아래 스크립트를 한 번 실행하세요.

```bash
bash scripts/doc-governance/install-hooks.sh
```

활성화 후에는 검증 실패 시 커밋이 중단되고, 경고 메시지가 출력됩니다.

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
