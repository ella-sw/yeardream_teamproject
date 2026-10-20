# 다음 구현 지시문 — M2 필수 탐지 유형

M0/M1의 첫 수직 흐름이 저장소에 구현되어 있다. 이번 시작점은 `docs/STATUS.md`의 현재 게이트와 인수 기준이다. 첫 흐름을 확인하지 않은 채 재구현하거나 4종 전체를 완료로 표시하지 않는다.

```text
먼저 AGENTS.md, IMPLEMENTATION_SPEC.md, ACCEPTANCE_TESTS.md,
docs/STATUS.md와 현재 Git 변경을 확인해줘. M0/M1의 C00~C02를 먼저
실행해 실제 수집→탐지→요소 위치→UI→result.json 회귀를 확인해줘.

이번 범위는 M2야.
- HOMOGLYPH, JAMO, TRANSPARENT의 명세된 사례를 구현하고,
  OFFSCREEN의 display:none 구현을 유지하며 다음 제안 조건을 추가해줘.
- 광고 의심 문맥과 은닉 기법 판단을 분리하고 정상 음성 사례를 함께 검증해줘.
- 동일 요소에 여러 기법이 실제 적용되면 technique별로 별도 결과를 내고,
  URL·location·technique 조합의 중복은 제거해줘.
- 정답 JSON은 tests/expected/에서만 읽어. 제품 코드는 테스트 정답이나
  테스트용 id를 보지 않아야 해.
- 변경 후 관련 D01~D15, N01~N08 및 M0/M1 회귀를 실행하고
  docs/TEST_REPORT.md와 docs/STATUS.md에 증거·한계를 기록해줘.

하위 페이지·iframe이 미완성이면 M3를 완료로 표시하지 마. Windows에서
실행하지 못하면 NOT RUN으로 남겨줘. 외부 광고 사이트를 임의 방문하거나
로그인·버튼 클릭·폼 제출을 하지 말고 자체 테스트 서버를 사용해줘.
```

## 팀원별 독립 검증

공통 데이터 계약을 바꾸기 전에 소비 모듈 영향을 확인한다. 서로 다른 브랜치/작업 디렉터리에서만 위임하며 같은 파일을 동시에 수정하지 않는다.

**탐지 품질 담당**

```text
M2의 광고 문맥·HOMOGLYPH/JAMO/TRANSPARENT·OFFSCREEN 사례를
독립 테스트 자료로 검증해줘. 정상 안내·경고·보도와 숨김 광고를 대조하고,
같은 요소의 중첩 기법 및 분할 텍스트 경계를 확인해줘. 내 소유 파일은
tests/expected/ 및 app/detection/ 테스트 자료이며 구현자 파일은 되돌리지 마.
실제값/기대값/차이와 재현 방법을 보고해줘.
```

**결과·실행 품질 담당**

```text
M2의 결과 UI와 JSON이 원문 근거, 중복 제거, 실제 DOM 위치를 유지하는지
검증해줘. 테스트 selector가 한 요소만 가리키는지 Playwright로 재조회하고,
Windows 환경이 없으면 NOT RUN으로 남겨줘. 내 소유 범위는 app/result/,
app/static/의 관련 출력·표시 코드와 독립 검증이며, 다른 변경을 되돌리지 마.
```
