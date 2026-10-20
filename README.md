# 공공 웹사이트 불법광고 탐지 도구

사용자가 권한을 가진 공공 웹사이트를 점검해 광고 의심 콘텐츠와 은닉 기법을 표시하는 Windows 로컬 도구입니다. 현재 코드는 **M0/M1 첫 세로 흐름**입니다. 입력한 페이지 한 곳에서 `display:none`으로 숨긴 광고 문맥을 `OFFSCREEN`으로 찾아 실제 요소 위치, 결과 UI, `result.json`까지 연결합니다.

## 현재 구현 범위

- URL 하나를 검사하며 하위 링크와 iframe은 아직 탐색하지 않습니다.
- 현재 작동하는 기법은 `display:none` 기반 `OFFSCREEN`뿐입니다. 다른 필수 기법은 다음 단계에서 추가합니다.
- 광고 문맥은 `app/detection/terms.json`의 도메인·홍보 용어가 같은 요소 안에 함께 있을 때만 후보로 봅니다. 이 작은 사전은 실증 검증된 분류기가 아닙니다.
- 결과는 실행 폴더의 `result.json`과 진단용 `run_report.json`에 저장됩니다. 작업별 사본은 `.runs/`에, 이전 최신 파일은 `.history/`에 보관합니다.
- 검사는 별도 프로세스에서 실행하고, UI는 `127.0.0.1`에만 바인딩합니다.
- 비공개·loopback·link-local 등 비공개 주소는 기본 차단합니다. `SCANNER_ALLOWED_TEST_ORIGINS`는 자체 테스트 중 정확한 origin만 허용할 때만 지정합니다. 이 설정은 사용자 입력으로 받지 않습니다.

이 도구는 법적 위법성을 확정하지 않고 의심 요소를 검토 대상으로 제시합니다. 실제 사이트를 검사하기 전에 점검 권한을 확보하세요.

## macOS 개발 실행

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python launcher.py
```

기본 브라우저에서 `http://127.0.0.1:8765`가 열립니다. Windows 패키지는 Windows PC에서 `scripts/build_windows.ps1`로 빌드해야 합니다. 자세한 실행 환경과 제한은 [`docs/BUILD.md`](docs/BUILD.md)를 참고하세요.

## 테스트

```bash
python -m pytest -q -s
```

테스트는 예약된 가상 문구를 포함한 자체 localhost 페이지만 검사합니다. 테스트가 만든 `result.json`과 현재 검증 상태는 [`docs/TEST_REPORT.md`](docs/TEST_REPORT.md), [`docs/STATUS.md`](docs/STATUS.md)에 기록합니다.

## 기준 문서

- [`IMPLEMENTATION_SPEC.md`](IMPLEMENTATION_SPEC.md): 제품 범위, 데이터 계약, 오류·안전 경계, 완료 게이트
- [`ACCEPTANCE_TESTS.md`](ACCEPTANCE_TESTS.md): 인수 기준
- [`AGENTS.md`](AGENTS.md): 저장소 작업 지침
- [`sources/contest-guidelines.pdf`](sources/contest-guidelines.pdf): 모집요강 원본
- [`sources/project-wiki.md`](sources/project-wiki.md): 팀 WIKI 원본
