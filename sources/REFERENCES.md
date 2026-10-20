# 출처와 적용 범위

## 사용자가 제공한 원본

[R1] `contest-guidelines.pdf`

원본: 「공공 웹사이트 불법광고 탐지 도구 개발 공모전 모집요강」, 18쪽.
필수 기능(p.5), 평가(p.6~7), 환경(p.8~9), 결과 스키마(p.10~14), 제출 서식(p.15~18)의 기준이다.
첨부 원문을 복사했으며, 이후 공고 변경 유무를 여기서 확인한 것은 아니다.

[R2] `project-wiki.md`

원본: 사용자가 업로드한 「공공 웹사이트 불법광고 탐지 도구」 WIKI 문서.
FastAPI 기반 구조와 Developer A / AI Analyst / Developer B의 모듈 구분을 유지했다.
4일 일정, 세부 기본값, 데이터 계약, 인수 테스트와 결과 책임 추가는 이번 명세의 제안이다.

과거 대화의 Tkinter 기반 간략안과 이번 WIKI가 다른 부분은 최신 사용자 WIKI 구조를 채택했다.
원본 파일을 고친 것은 아니다. 모호한 공모전 조건은 명세 §13에 남겼다.

## 구현을 위해 별도로 확인한 공식 기술 자료

아래 자료는 공모전 규정의 출처가 아니라 기술 구현 참고다. 확인일: 2026-10-20.
배포 시점의 설치 버전/API 지원은 구현 환경에서 다시 확인한다.

[T1] OpenAI — Custom instructions with AGENTS.md
`https://developers.openai.com/codex/agent-configuration/agents-md`
Codex의 저장소 지침 파일 읽기 방식. 기존 AGENTS.override.md나 하위 폴더 지침이 있을 수 있으므로 기존 규칙을 먼저 확인한다. 다른 에이전트의 자동 인식은 전제하지 않고, 시작 프롬프트에서도 파일 읽기를 명시한다.

[T2] Playwright Python — Frames
`https://playwright.dev/python/docs/frames`
프레임 단위 접근의 구현 참고.

[T3] MDN — Window.getComputedStyle
`https://developer.mozilla.org/en-US/docs/Web/API/Window/getComputedStyle`
적용된 스타일 조회 참고. 이것만으로 모든 시각적 은닉을 해결한다는 의미는 아니다.

[T4] Unicode UAX #15 — Unicode Normalization Forms
`https://www.unicode.org/reports/tr15/`
정규화의 의미와 한계 참고.

[T5] Unicode UTS #39 — Unicode Security Mechanisms
`https://www.unicode.org/reports/tr39/`
닮은꼴 문자 처리 참고. 사용하는 데이터/라이선스/버전은 실제 구현에서 기록한다.

[T6] Playwright Python — Library / PyInstaller / Known issues
`https://playwright.dev/python/docs/library`
브라우저 번들, 동기/비동기 실행, Windows 이벤트 루프·스레드 관련 주의점 참고.

[T7] PyInstaller Manual
`https://pyinstaller.org/en/stable/`
운영체제별 빌드 및 독립 배포 참고. Windows 산출물은 Windows에서 빌드해야 한다.

[T8] OWASP — Server Side Request Forgery Prevention Cheat Sheet
`https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html`
URL/네트워크 검증 설계 참고. 앱 수준 검증만으로 모든 네트워크 공격을 막았다고 주장하지 않는다.

[T9] Playwright Python — Evaluating JavaScript
`https://playwright.dev/python/docs/evaluating`
페이지 내부 DOM/스타일 추출을 실행 환경으로 가져오는 방법 참고.
