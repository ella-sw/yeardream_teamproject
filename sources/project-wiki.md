WIKI 프로젝트 문서

# 공공 웹사이트 불법광고 탐지 도구

> 공공 웹사이트의 게시·은닉된 불법광고를 자동으로 탐지하고, 탐지 유형과 위치를 확인할 수 있는 도구

---

# 1. Project Overview

## 1.1 프로젝트 목표

사용자가 점검할 웹사이트 URL을 입력하면 해당 URL을 시작으로 웹사이트의 다양한 영역을 탐색하여 불법광고를 탐지한다.

### 탐색 대상

- 하위 페이지
- 게시글
- 댓글
- 페이지 내 iframe
- iframe 내부 요소

### 필수 탐지 유형

| 유형 | 코드 | 설명 |
|---|---|---|
| 닮은꼴 글자 위장 | `HOMOGLYPH` | 유사하게 생긴 문자를 이용한 필터링 우회 |
| 자모 분해 | `JAMO` | 한글 음절을 자모 단위로 분해하여 키워드 매칭 우회 |
| 투명 텍스트 | `TRANSPARENT` | 배경색, `opacity:0`, `color:transparent` 등을 이용한 은닉 |
| 화면 밖 은닉 | `OFFSCREEN` | `font-size`, `position`, `display:none` 등을 이용한 은닉 |

> 위 4개 탐지 유형은 공모전 적격평가 대상이므로 프로젝트의 핵심 기능으로 취급한다.

---

# 2. Project Scope

## 2.1 핵심 기능

```text
URL 입력
   ↓
웹사이트 탐색
   ↓
페이지 / 게시글 / 댓글 / iframe 탐색
   ↓
DOM 및 콘텐츠 분석
   ↓
불법광고 탐지
   ↓
탐지 유형 분류
   ↓
정확한 위치 식별
   ↓
탐지 결과 생성
   ↓
결과 화면 + result.json
```

## 2.2 사용자에게 제공하는 기능

- 점검 대상 URL 입력
- 탐지 실행
- 탐지 진행 상태 확인
- 탐지 결과 확인
- 탐지 유형 확인
- 탐지 위치 확인
- 검출 근거 확인
- 전체 탐지 결과 관리

## 2.3 공모전 필수 결과물

### `result.json`

적격평가에 사용되는 필수 결과 파일.

### `result_extra.json`

필수 4종 외 추가 탐지 유형을 구현한 경우 생성한다.

---

# 3. System Architecture

```text
┌──────────────┐
│    사용자     │
└──────┬───────┘
       │ URL
       ▼
┌──────────────┐
│   Frontend   │
└──────┬───────┘
       ▼
┌──────────────┐
│   FastAPI    │
└──────┬───────┘
       ▼
┌──────────────────────┐
│    Web Crawler       │
│                      │
│ - 하위 페이지        │
│ - 게시글             │
│ - 댓글               │
│ - iframe             │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│   Detection Engine   │
│                      │
│ HOMOGLYPH            │
│ JAMO                 │
│ TRANSPARENT          │
│ OFFSCREEN            │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│   Result Builder     │
│                      │
│ URL                  │
│ Location             │
│ Evidence             │
│ Technique            │
└──────────┬───────────┘
           ▼
      ┌────┴─────┐
      ▼          ▼
  result.json   결과 UI
```

> 위 구조는 프로젝트 구현을 위한 팀 제안 구조이며, 모집요강에서 특정 프레임워크나 아키텍처를 요구하는 것은 아니다.

---

# 4. TEAM ROLE

## 👨‍💻 AI Service Developer A
### Web Crawling & Backend

**주요 책임**

웹사이트를 실제로 탐색하고 Detection Engine에 분석할 데이터를 전달하는 영역을 담당한다.

### 담당 업무

- Frontend ↔ Backend 연결
- FastAPI 구성
- URL 입력 처리
- 웹페이지 탐색
- 하위 페이지 탐색
- 게시글 탐색
- 댓글 영역 탐색
- iframe 탐색
- iframe 내부 요소 탐색
- 크롤링 결과 전달
- 탐색 과정에서 발생하는 예외 처리
- 탐색 결과와 Detection Engine 연결

### 최종 담당 영역

```text
URL 입력
   ↓
FastAPI
   ↓
Crawler
   ↓
탐색 데이터
```

---

# 5. TEAM ROLE

## 👨‍💻 AI Service Developer B
### Detection Integration & Result/UI

**주요 책임**

Detection Engine의 결과를 실제 공모전 제출 형식으로 연결하고 사용자에게 보여주는 영역을 담당한다.

### 담당 업무

- DOM 분석 결과 처리
- Detection Engine 연동
- 탐지 요소의 정확한 위치 식별
- CSS Selector 생성
- iframe 내부 Selector 처리
- 탐지 결과 데이터 구조화
- `result.json` 생성
- 결과 화면 구현
- 탐지 결과 필터링/확인 기능
- Backend ↔ Frontend 통합

### 최종 담당 영역

```text
Detection Engine
       ↓
탐지 결과
       ↓
CSS Selector
       ↓
Result Builder
       ↓
result.json
       ↓
결과 UI
```

---

# 6. TEAM ROLE

## 🤖 AI Analyst
### Detection Logic & Validation

**주요 책임**

공모전의 핵심 탐지 유형을 실제 탐지 로직으로 구현하고 검증한다.

### 담당 업무

#### 필수 탐지

- `HOMOGLYPH`
- `JAMO`
- `TRANSPARENT`
- `OFFSCREEN`

#### 검증

- 탐지 조건 정의
- 테스트 데이터 구성
- 정상/불법광고 사례 비교
- 오탐 검증
- 미탐 검증
- 탐지 결과 정확도 개선
- Detection Engine과 개발자 영역의 연동 검증

### 최종 담당 영역

```text
웹페이지 분석 데이터
       ↓
Detection Logic
       ↓
탐지 여부
       ↓
Technique
       ↓
검증
```

---

# 7. ROLE 연결 구조

세 역할은 독립적으로 끝나는 것이 아니라 다음과 같이 연결한다.

```text
AI Service Developer A
[Web Crawling]
        │
        ▼
  분석 대상 데이터
        │
        ▼
AI Analyst
[Detection Logic]
        │
        ▼
   탐지 결과
        │
        ▼
AI Service Developer B
[Result / UI]
        │
        ├── result.json
        │
        └── 결과 화면
```

### 역할 구분 기준

| 역할 | 핵심 책임 |
|---|---|
| Developer A | **찾아온다** |
| AI Analyst | **판단한다** |
| Developer B | **정리해서 보여준다** |

---

# 8. Detection Requirements

## HOMOGLYPH

유사하게 생긴 문자 등을 이용하여 사람이 보기에는 동일하거나 유사하지만 필터링 시스템을 우회하는 방식.

## JAMO

한글 음절을 자모 단위로 분해하여 키워드 매칭을 우회하는 방식.

## TRANSPARENT

텍스트와 배경을 동일한 색상으로 설정하거나 `opacity:0`, `color:transparent` 등을 이용하여 시각적으로 숨기는 방식.

## OFFSCREEN

화면에서 보이지 않도록 요소를 숨기는 방식.

모집요강에서 제시한 예시는 다음과 같다.

- `font-size: 0~1px`
- `position:absolute; left:-9999px`
- `display:none`

---

# 9. Detection Result

하나의 탐지 결과는 다음 조합을 기준으로 관리한다.

```text
URL
+
Location
+
Technique
```

동일한 요소에 여러 탐지 기법이 적용된 경우에는 **기법별로 별도의 결과를 생성**한다.

예:

```text
Finding 1
URL: ...
Location: ...
Technique: JAMO

Finding 2
URL: ...
Location: ...
Technique: TRANSPARENT
```

---

# 10. Location Rule

탐지된 요소의 위치는 CSS Selector를 이용하여 식별한다.

### 기본 형태

```text
div.notice-board > span.visually-hidden
```

### 클래스가 없는 경우

```text
tr:nth-of-type(7)
```

### iframe 내부

```text
iframe[src="https://example.com/widget"]
>>> div.wrap > span.hidden-link
```

iframe이 여러 단계로 중첩된 경우 `>>>`를 반복한다.

### 중요

Selector는 단순히 문자열 형식만 맞추는 것이 아니라 **실제 동일한 웹페이지 요소를 정확하게 가리켜야 한다.**

하나의 Selector가 여러 요소를 가리키는 경우 정확한 위치를 특정할 수 없으므로 문제가 될 수 있다.

---

# 11. Result JSON

## 기본 구조

```text
meta
├── topic
├── entry_url
├── started_at
├── finished_at
├── elapsed_sec
└── tool_version

findings[]
├── id
├── url
├── is_violation
├── location
├── evidence_text
└── technique
```

## 필수 Technique

```text
HOMOGLYPH
JAMO
TRANSPARENT
OFFSCREEN
```

## 결과가 없는 경우

`findings`는 반드시 빈 배열로 생성한다.

```text
"findings": []
```

---

# 12. 결과 정확도 핵심

공모전 적격평가에서는 다음 세 가지가 모두 중요하다.

```text
URL
+
Location
+
Technique
```

세 필드가 정답셋과 일치해야 정답 검출로 인정된다.

### 따라서 개발 우선순위

```text
① 탐지 건수를 최대한 확보
        ↓
② 탐지 유형 정확하게 분류
        ↓
③ 정확한 DOM 위치 확보
        ↓
④ 올바른 result.json 생성
```

`evidence_text`는 정답 판정에는 사용되지 않지만 본심사 참고자료로 활용되므로 반드시 작성한다.

---

# 13. User Interface

## 기본 화면

```text
┌─────────────────────────────────────┐
│ 불법광고 탐지 도구                  │
├─────────────────────────────────────┤
│                                     │
│ URL                                 │
│ [ https://example.go.kr          ]  │
│                                     │
│              [ 탐지 시작 ]          │
│                                     │
└─────────────────────────────────────┘
```

## 탐지 결과

```text
┌─────────────────────────────────────┐
│ 탐지 결과                            │
├─────────────────────────────────────┤
│ 총 탐지 건수                         │
│ 12건                                 │
├─────────────────────────────────────┤
│ HOMOGLYPH       4건                  │
│ JAMO            3건                  │
│ TRANSPARENT     2건                  │
│ OFFSCREEN       3건                  │
├─────────────────────────────────────┤
│ URL                                  │
│ 탐지 위치                            │
│ 탐지 유형                            │
│ 검출 근거                            │
└─────────────────────────────────────┘
```

> 실제 화면 구성은 개발 과정에서 변경할 수 있다. 핵심은 사용자가 탐지 결과와 근거를 쉽게 확인할 수 있도록 구성하는 것이다.

---

# 14. 공모전 핵심 / 선택 기능

## 🔴 Core

공모전 제출을 위해 우선적으로 완성해야 하는 영역.

- URL 입력
- 웹사이트 탐색
- 하위 페이지 탐색
- 게시글 탐색
- 댓글 탐색
- iframe 탐색
- HOMOGLYPH
- JAMO
- TRANSPARENT
- OFFSCREEN
- 위치 식별
- CSS Selector
- 결과 UI
- `result.json`

---

## 🟡 Optional

공모전 핵심 기능이 안정적으로 완성된 이후 추가 검토한다.

### RAG

탐지 결과에 대한 설명이나 불법광고 유형 안내 등에 활용 가능.

예:

> HOMOGLYPH란 무엇인가?

> 이번 결과가 왜 HOMOGLYPH로 분류되었는가?

### LangChain

RAG 등의 AI 기능을 구성할 필요가 있을 경우 선택적으로 활용.

### LangGraph

여러 단계의 AI Workflow가 실제로 필요한 경우 선택적으로 활용.

### DB

탐지 이력, 사용 기록 등 별도 관리가 필요한 경우 선택적으로 활용.

---

# 15. Optional 기능의 적용 원칙

> **Optional 기능은 공모전 핵심 기능을 대체하지 않는다.**

우선순위는 다음과 같다.

```text
공모전 필수 기능
      ↓
탐지 정확도
      ↓
result.json 안정성
      ↓
결과 UI / 실무 활용성
      ↓
추가 탐지 유형
      ↓
팀플 교육과정 기술
(RAG / LangChain / LangGraph / DB 등)
```

팀플 교육과정에 필요한 기술은 **핵심 기능이 안정적으로 동작하고 추가 작업이 가능한 경우 AI Analyst를 중심으로 선택적으로 적용한다.**

---

# 16. Git / GitHub 협업

## Repository 기본 구조

```text
project/
├── frontend/
├── backend/
├── crawler/
├── detection/
├── result/
├── tests/
├── docs/
├── README.md
└── ...
```

실제 디렉터리 구조는 개발 과정에서 조정할 수 있다.

## Branch 예시

```text
main
├── feat/crawler
├── feat/detection
├── feat/result
└── feat/frontend
```

## 기본 협업 흐름

```text
Issue
 ↓
Branch 생성
 ↓
개발
 ↓
Commit
 ↓
Pull Request
 ↓
Review
 ↓
Merge
```

---

# 17. 개발자 간 연결 규칙

각 담당자가 자신의 기능만 완성하는 것이 아니라 **기능 간 연결 지점을 먼저 맞춘다.**

### Crawler → Detection

```text
Crawler
   ↓
페이지 정보
DOM 정보
iframe 정보
   ↓
Detection Engine
```

### Detection → Result

```text
Detection Engine
   ↓
url
location
evidence_text
technique
   ↓
Result Builder
```

### Result → UI

```text
Result Builder
   ↓
탐지 결과
   ↓
Frontend
```

> 세 영역의 데이터 형식은 초기에 합의하고 이후 임의로 변경하지 않는다.

---

# 18. Final Checklist

## Core

- [ ] URL 입력
- [ ] 웹사이트 탐색
- [ ] 하위 페이지 탐색
- [ ] 게시글 탐색
- [ ] 댓글 탐색
- [ ] iframe 탐색
- [ ] HOMOGLYPH 탐지
- [ ] JAMO 탐지
- [ ] TRANSPARENT 탐지
- [ ] OFFSCREEN 탐지
- [ ] CSS Selector 생성
- [ ] 탐지 결과 UI
- [ ] `result.json` 생성

## Result

- [ ] `meta` 정상 생성
- [ ] `findings` 정상 생성
- [ ] `url` 정상 생성
- [ ] `location` 정상 생성
- [ ] `evidence_text` 정상 생성
- [ ] `technique` 정상 생성
- [ ] UTF-8 / BOM 없음
- [ ] JSON 파싱 가능
- [ ] 중복 결과 처리
- [ ] iframe Selector 처리

## Submission

- [ ] Windows 11 실행 가능
- [ ] 실행 파일
- [ ] 전체 소스코드
- [ ] 실행/빌드 매뉴얼
- [ ] 사용설명서
- [ ] 필요한 경우 `.env` 외부 설정
- [ ] 제출 파일 누락 여부 확인

---
