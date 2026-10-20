# M0/M1 자체 테스트 보고서

검사한 커밋: `1a4b42f879fd9539c2c2337fe3d14ffccba8b408` (`feat/m0-m1-first-scan`)

## 실행 환경

- OS / CPU / RAM: macOS 27.0 / arm64 / 16 GiB
- Python: 3.14.3
- FastAPI / Playwright Python / Chromium: 0.150.0 / 1.64.0 / 156.0.8078.4
- 실행 명령: `.venv/bin/python -m pytest --basetemp=/tmp/yeardream_m0m1_test_results_final -q -s`
- 결과: **12 passed in 6.56s**
- 문법 확인: `.venv/bin/python -m compileall -q app tests launcher.py` 성공

## 인수 기준 결과

| ID | 결과 | 실제 증거 |
|---|---|---|
| C00 | PASS | Chromium 156.0.8078.4 실행, 페이지 열기, 정상 종료 확인 |
| C01 | PASS | 자체 localhost 페이지 1개에서 기대 1건 / 검출 1건. 선택자가 요소 1개만 가리키고 태그·원문이 일치함 |
| C02 | PASS | 실제 Chromium UI에서 URL 입력·검사 시작·완료·결과 표시. `result.json` 파싱·팀 JSON Schema 검증 통과, UTF-8 BOM 없음 |
| 안전 URL 검사 | PASS | `file:`, `javascript:`, 사용자 정보 포함 URL, loopback/localhost, port 0 거부; 테스트용 정확한 localhost origin 허용; 앱 제어 UI origin은 허용 목록에 있어도 거부 |
| 빈 결과 출력 | PASS | `findings: []` 결과가 스키마를 통과 |
| W01~W04 | NOT RUN | Windows 11 실행 환경 없음 |

테스트용 기대 결과는 `tests/expected/m1_findings.json`에 두며 제품 코드는 이를 읽지 않습니다. fixture는 `tests/fixtures_site/index.html`의 가상 문구이며 실제 광고 사이트를 방문하지 않았습니다.

## 생성 결과 파일

- 실행 출력: `/tmp/yeardream_m0m1_test_results_final/test_c02_actual_ui_scan_create0/output/result.json`
- 진단 출력: `/tmp/yeardream_m0m1_test_results_final/test_c02_actual_ui_scan_create0/output/run_report.json`
- 실제 검출: `OFFSCREEN` 1건, 원문 `카지노 가입 보너스 안내`, 선택자 `body > main > span.promo-hidden`
- 결과 `elapsed_sec`: 1.114초. 자체 1페이지 테스트에서 관찰한 값이며 공모전 처리 시간이나 실제 탐지 성능을 뜻하지 않음.

## 미검증 및 남은 한계

- Windows 11 패키지 빌드·Python/Playwright 캐시 없는 실행·공백/한글 경로·연속 실행은 확인하지 않았습니다.
- 현재 스캐너는 진입 페이지 1개와 `display:none` 기반 `OFFSCREEN`만 처리합니다. 하위 페이지, 게시글·댓글 탐색, iframe, 나머지 3종은 아직 구현하지 않았습니다.
- 광고 문맥 사전은 테스트 시작용 제안 규칙이며 정확도 검증 묶음이 아닙니다. 법적 위법성을 판정하지 않습니다.
- 네트워크 주소 검사와 브라우저 요청 차단은 방어층입니다. OS 수준 격리나 DNS rebinding 완전 방지를 보장하지 않습니다.
