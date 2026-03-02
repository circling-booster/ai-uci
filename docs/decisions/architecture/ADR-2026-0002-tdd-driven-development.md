---
id: ADR-2026-0002-tdd-driven-development
title: TDD 기반 개발 원칙 채택
status: Accepted
domain: architecture
date: 2026-03-02
owner: architecture-team
reviewer: tech-lead
approver: cto
related_adrs:
  - ADR-2026-0001-hexagonal-architecture
related_reports: []
related_visions: []
supersedes: []
superseded_by: []
risk_owner: architecture-team
tags: [testing, quality, tdd]
---

# ADR-2026-0002: TDD 기반 개발 원칙 채택

## 1) 배경
- 헥사고날 아키텍처를 적용하면 도메인 중심으로 분리되지만, 구현 안정성은 테스트 전략이 받치는 정도가 큼.
- 현재는 기능 개발 후 테스트 작성이 선행되지 않는 경우가 있어, 리팩터링 시 회귀 탐지가 늦어짐.

## 2) 결정 필요성
- 도메인 규칙 변경과 리팩터링이 빈번한 프로젝트에서는 RED-GREEN-REFACTOR 루프 기반의 개발 규율이 필수.
- 테스트 미완성으로 인한 의도치 않은 경계 위반/회귀를 줄이기 위해 TDD 원칙을 ADR 레벨에서 고정해야 함.

## 3) 대안
### 대안 A: 코드 구현 후 사후 테스트 강화
- 장점: 초기 속도 빠름
- 단점: 회귀 누락, 테스트 품질 저하 위험

### 대안 B: TDD 의무화
- 장점: 핵심 행위 정의/검증이 선행되고 리팩터링 비용이 낮아짐
- 단점: 초기 단계 학습 및 템플릿 비용

### 대안 C: 중요 모듈만 TDD 대상
- 장점: 도입 장벽 낮음
- 단점: 모범 사례가 모듈별 편차로 흩어짐

## 4) 결정
- 프로젝트의 표준 개발 원칙으로 **TDD를 채택**한다.
- 적용 규칙
  - RED-GREEN-REFACTOR 순서를 모든 신규 비즈니스 기능 개발의 기본 흐름으로 채택
  - 외부 의존은 Mock/Stub 또는 Fake Adapter로 격리 후 테스트
  - 리팩터링은 인덱싱된 회귀 케이스를 깨뜨리지 않는 범위에서 수행

## 5) 영향도
### 기대 효과
- 의사결정 규칙(헥사고날 경계) 위반을 테스트로 조기에 탐지
- 변경 시 안정적으로 기존 동작 유지

### 위험/트레이드오프
- 초기 학습 곡선 상승
- 테스트 범위 논의/리뷰 비용 증가

## 6) 적용 계획
- [x] ADR 메타데이터 규칙 적용 (완료)
- [ ] 각 도메인 기능에 대한 `Given/When/Then` 시나리오 템플릿 정착
- [ ] 커버리지 게이트(필요 최소 임계값) 운영 규칙 확정
- [ ] PR 템플릿 및 리뷰 체크리스트에 TDD 항목 추가
- [ ] 리팩터링 전/후 회귀 검증 체크리스트를 CI에 반영
- 소유자: architecture-team
- 완료 예정일: 2026-03-22

## 7) 성공 기준
- 정량: 신규 핵심 기능 PR에서 테스트 우선 작성률 100%
- 정성: 코드 리뷰에서 TDD 준수 미준수 항목 재발률 저하

## 8) 참조
- 관련 비전: []
- 관련 리포트: []
- 관련 ADR: [ADR-2026-0001-hexagonal-architecture]
