# Reports 저장소

`docs/reports`는 ADR(결정)을 뒷받침하는 분석 및 근거 문서 저장소이다.

## 목적
- Why/분석/리스크를 기록해 Decision의 품질을 높인다.
- 시간축과 주제축에서 문서를 빠르게 검색 가능하게 한다.

## 규칙
- 파일명 형식: `RPT-YYYY-PP-NNNN-슬러그.md` (영문 소문자, 숫자, 하이픈만 허용)
  - PP: 분기(Q1~Q4) 또는 월(M01~M12) 중 하나 사용
  - 예: `RPT-2026-Q1-0001-architecture-technical-decision.md`
- 유형: `strategic | technical | legal | product | market | risk | compliance`
- 상태: `Draft | Reviewed | Approved`
- `related_adrs`는 필수 메타데이터 필드이며 형식만 검증됩니다.
- 실제 검토 추적성 강화를 위해 관련 ADR를 최소 1개 이상 링크할 것을 권장합니다(현재 스키마/검증은 빈 배열도 허용).
- `도메인`(`business | product | compliance | architecture | legal | engineering | strategy`)과
  `유형(type)`은 독립 축으로 관리한다.
- `by-domain/<domain>/...` 또는 `by-quarter/YYYY-Qn/...` 경로와 `domain/period`가 일치해야 한다.
- 파일명은 `id`와 동일해야 하며, `id` 및 파일명은 ASCII 소문자 slug만 허용한다.

## YAML Front Matter (필수)

모든 리포트 본문은 아래 필드를 YAML front matter로 시작해야 한다.

- `id` (예: `RPT-2026-Q1-0001-architecture-review`)
- `title`
- `status`
- `type`
- `date` (`YYYY-MM-DD`)
- `period` (`YYYY-Q1` ~ `YYYY-Q4` 또는 `YYYY-M01` ~ `YYYY-M12`)
- `domain` (`business | product | compliance | architecture | legal | engineering | strategy`)
- `owner`
- `reviewer`
- `approver`
- `related_adrs` (배열)

선택 필드:
- `risk_owner`
- `tags` (배열)
- `quarter` (deprecated alias, 사용 시 경고)

운영 규칙:
- `docs/reports/metadata-schema.yaml` 스펙을 기준으로 스크립트 검증 대상이다.
- `docs/reports/registry/reports-index.md`는 생성기로 갱신한다.
- 같은 문서는 `by-domain/<domain>` 또는 `by-quarter/<period>` 하위에 위치해야 한다.
- by-quarter 경로는 기존 `YYYY-Qn` 형태를 유지한다.
- 생성 규칙은 동일 정렬(시간/상태/ID) 기준을 따른다.

## 검증 및 인덱스
- `scripts/doc-governance/validate.py --check`로 메타데이터/형식/교차참조 검증
- `scripts/doc-governance/validate.py --generate-index`로 `docs/reports/registry/reports-index.md` 재생성

### 로컬 커밋 검사 (권장)

`docs/reports` 경로의 변경을 커밋할 때마다 자동 검증하려면 아래를 한 번 실행하세요.

```bash
bash scripts/doc-governance/install-hooks.sh
```

검증 실패 시 커밋이 차단되고, 콘솔에 경고 메시지가 출력됩니다.

## 폴더 역할
- `by-domain/`: 기술/법무/제품/비즈니스/전략/컴플라이언스 주제별 분류
- `by-quarter/`: 연도-분기 기준 아카이브
- `registry/`: 인덱스
- `templates/`: 리포트 템플릿
