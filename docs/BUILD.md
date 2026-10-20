# 실행·빌드 안내

## 개발 실행

현재 개발 환경 기준은 macOS arm64, Python 3.14.3, Playwright Python 1.64.0, Chromium 156.0.8078.4입니다. Python과 직접 의존성은 `requirements.txt`, 개발·검증 도구는 `requirements-dev.txt`에서 고정합니다.

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python launcher.py
```

서버는 `127.0.0.1:8765`에만 열고 검사 UI를 기본 브라우저로 표시합니다. `SCANNER_OUTPUT_DIR`을 지정하면 결과 저장 폴더를 바꿀 수 있으며, API 요청으로 임의 경로를 전달할 수는 없습니다.

## 자체 테스트 사이트 허용

기본 정책은 loopback, 사설, link-local, 비전역 주소를 거절합니다. 로컬 테스트에서만 정확한 fixture origin을 허용합니다.

```bash
SCANNER_ALLOWED_TEST_ORIGINS=http://127.0.0.1:49152 python -m pytest -q
```

실제 포트는 테스트 서버가 매번 임의로 정하므로 테스트 fixture가 이 값을 프로세스에 설정합니다. 사용자 대상 실행에서 이 변수를 지정하지 마세요. 도메인 확인과 브라우저 요청 차단은 방어층이지 네트워크 격리나 DNS rebinding 완전 방지로 간주하지 않습니다.

## Windows 11 패키징

실행 파일은 Windows에서 빌드해야 합니다. PyInstaller는 교차 컴파일러가 아니므로 macOS 빌드 결과를 Windows 배포물로 사용하지 않습니다.

Windows PowerShell에서 저장소 루트 기준으로 실행합니다.

```powershell
.\scripts\build_windows.ps1
```

스크립트는 Python 3.14 가상환경을 만들고 고정 의존성·Chromium을 설치한 뒤 `dist\PublicAdInspector`에 `onedir` 산출물을 생성합니다. 사용자 폴더로 산출물 전체를 복사해 실행합니다. 첫 Windows 빌드와 Python·Playwright 캐시가 없는 Windows 11 실행은 아직 확인하지 않았습니다.
