# ADR (Architecture/Decision) 저장소

`docs/decisions`는 **의사결정 기록(ADR)**을 관리한다.

## 목적
- 무엇을 언제, 왜 결정했는지 추적 가능하게 남긴다.
- 제품/아키텍처/법무/운영 판단의 근거를 단일 체계로 관리한다.

## 규칙
- 필수 메타데이터는 `docs/decisions/metadata-schema.yaml`를 따른다.
- 파일명 형식: `ADR-YYYY-NNNN-슬러그.md` (영문 소문자, 숫자, 하이픈만 허용)
  - 예: `ADR-2026-0001-hexagonal-architecture.md`
  - 파일명은 `id`와 동일해야 하며 확장자는 `.md`만 허용한다.
- 상태: `Proposed`, `Accepted`, `Deprecated`, `Superseded`
- `related_adrs`/`related_reports`/`related_visions`는 각 추적 참조 배열입니다.
- 최소 1개 이상 참조는 권장되며, 현재 검증은 빈 배열을 경고(WARN)로 처리합니다.
- 동일 도메인 내에서는 ID가 오름차순 정렬되도록 관리한다.

## YAML Front Matter (필수)

모든 ADR 본문은 아래 필드를 YAML front matter로 시작해야 한다.

- `id` (예: `ADR-2026-0001-local-first`)
- `title`
- `status`
- `domain` (`architecture | product | legal | platform | operations | deprecated`)
- `date` (`YYYY-MM-DD`)
- `owner`
- `reviewer`
- `approver`
- `related_adrs` (배열)
- `related_reports` (배열)
- `related_visions` (배열)

선택 필드:
- `supersedes` (배열)
- `superseded_by` (배열)
- `risk_owner`
- `tags` (배열)

운영 규칙:
- `id`, `date`, `status`, `domain`는 템플릿과 스키마를 기준으로 엄격 검사한다.
- `id`와 `status`는 경고/오류 규칙에 따라 스크립트 검증을 통과해야 한다.
- `docs/decisions/metadata-schema.yaml`를 기준으로 템플릿은 필수 필드/형식이 고정된다.

## 폴더 역할
- `architecture/`: 시스템 구조, 동작 모델, 데이터·확장성 관련 ADR
- `product/`: 기능 범위, MVP, 우선순위, UX 정책 관련 ADR
- `legal/`: ToS, 저작권, 개인정보, 컴플라이언스 관련 ADR
- `platform/`: 플랫폼 통합 정책, 어댑터 전략, 의존성 정책
- `operations/`: 배포, 운영, 보안, 성능/관측성 정책
- `deprecated/`: 폐기된 ADR 보관
- `templates/`: ADR 작성 템플릿
- `registry/`: 인덱스 및 ADR 추적표

## 검증 및 인덱스
- `scripts/doc-governance/validate.py --check`로 메타데이터/형식/교차참조 검증
- `scripts/doc-governance/validate.py --generate-index`로 `docs/decisions/registry/decisions-index.md` 재생성

### 로컬 커밋 검사 (권장)

`docs/decisions` 경로의 변경을 커밋할 때마다 자동 검증하려면 아래를 한 번 실행하세요.

```bash
bash scripts/doc-governance/install-hooks.sh
```

검증 실패 시 커밋이 차단되고, 콘솔에 경고 메시지가 출력됩니다.
