# 현재 상태와 다음 작업

## 사실

- 기준 브랜치: GitHub `master`; 인계 문서 PR #1은 2026-10-20에 병합됨.
- 구현 브랜치: `feat/m0-m1-first-scan`.
- 구현 커밋: `1a4b42f879fd9539c2c2337fe3d14ffccba8b408`.
- 개발 환경: macOS 27.0 arm64, Python 3.14.3, Playwright Python 1.64.0, Chromium 156.0.8078.4.
- 인수 테스트의 자체 fixture에서 실제 수집→`display:none` 탐지→유일한 요소 위치→UI→정식 JSON을 확인했다.
- 상세 명령·결과 파일·한계는 `docs/TEST_REPORT.md`에 기록했다.

## 게이트

| 단계 | 상태 | 증거 |
|---|---|---|
| M0 환경·데이터 계약·Windows 패키징 최소 경로 | PARTIAL | 버전 고정, spawn 검사 프로세스, 로컬 API/UI, Windows 빌드 스크립트 작성. Windows 빌드·실행 미검증 |
| M1 첫 실제 수집→탐지→UI→JSON | PASS (macOS 자체 fixture) | C00~C02 PASS; 정확한 결과와 12개 테스트 통과. Windows 결과는 아님 |
| M2 필수 4종·음성 사례 | NOT STARTED | HOMOGLYPH, JAMO, TRANSPARENT 및 나머지 OFFSCREEN 조건 미구현 |
| M3 사이트·프레임·위치 | NOT STARTED | 하위 페이지·게시글·댓글·iframe 미구현 |
| M4 실패 처리·Windows 검증 | NOT STARTED | Windows W01~W04 미실행; 추가 오류/취소 인수 검증 미완료 |
| M5 제출 동결 | NOT STARTED | 실행 파일과 제출 문서 미완료 |

## 팀 배정

- 통합·수집 책임자 A: 미정
- 탐지 품질 책임자: 미정
- 실행·출력 책임자 B: 미정
- Windows 검증 장비/담당자: 미정

## 미확인 사항

명세 §13의 U1~U5를 유지한다. Windows 11에서의 패키징·실행과 시험 PC 호환성을 확인하지 않았다. M1 구현은 첫 통합 흐름이며 광고 탐지의 정확도를 보장하지 않는다.

## 다음 한 작업

M2: C00~C02 회귀를 유지하면서 HOMOGLYPH, JAMO, TRANSPARENT와 OFFSCREEN의 명세 사례·정상 음성 사례를 구현·검증한다. M3의 하위 페이지/iframe은 완료로 표시하지 않는다.
