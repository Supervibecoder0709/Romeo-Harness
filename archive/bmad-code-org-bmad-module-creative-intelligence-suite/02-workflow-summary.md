# 워크플로우 요약

## 무엇을 하는가

CIS는 “아이디어를 빨리 내는 도구” 하나가 아니라, 문제 정의부터 검증·다음 행동까지 대화를 구조화하는 BMad용 prompt module이다. 실제로 구현된 로컬 workflow는 **Design Thinking**, **Innovation Strategy**, **Problem Solving**, **Storytelling** 4개다. Brainstorming은 Carson agent가 외부 skill을 메뉴에서 호출하는 구조이고, Presentation은 Caravaggio의 직접 prompt 메뉴만 확인된다. [E04][E05][E06]

## 공통 실행 계약

| 순서 | 입력 | 처리 단계 | 출력/상태 | 실패·재시도 | 관찰 증거 |
| --- | --- | --- | --- | --- | --- |
| 1. 활성화 | skill root, 프로젝트 `_bmad` 설정 | 기본 TOML → team override → user override 병합, prepend step 실행, persistent facts 로드 | 활성화된 workflow/agent context | resolver 실패 시 prompt가 정의한 수동 병합으로 전환 | resolver 성공 로그 또는 실제 병합 결과는 이 레포 밖이라 **미확인** |
| 2. 문맥 수집 | 사용자 대화, 선택적 `data` 파일, `config.yaml` | 사용자의 과제·제약·성공 기준을 질문하고 CSV 방법론/Template을 로드 | 각 workflow의 초안 컨텍스트 | 없는 persistent file/glob은 지시상 조용히 건너뜀 | 채팅 내용, 선택된 방법론, 로드 파일 목록 |
| 3. 단계 실행 | 사용자의 응답 | workflow별 질문→분석→`<template-output>` | 현재 산출물 초안 | 각 checkpoint마다 사용자가 Continue/Advanced Elicitation/Party-Mode/YOLO 중 다음 행동을 선택 | 표시된 checkpoint와 저장 경로 |
| 4. 저장·완료 | template placeholder 값 | default output path에 구조화 Markdown을 갱신하고, 완료 hook을 해석 | `{output_folder}` 아래 Markdown | `on_complete`가 비어 있지 않으면 추가 terminal instruction을 따른다고 지시 | 실제 파일 존재·내용·해시가 완료 증거. 이 아카이브에서는 실행하지 않아 **미확인** |

이 표의 1·4는 실행 코드가 아니라 skill의 지시문 근거다. 호스트가 이를 실제로 강제하는지는 별도 BMad 통합 테스트로 검증해야 한다. [E05][E06]

## 1) Design Thinking

**입력:** 설계 과제, 사용자/이해관계자, 제약, 성공 기준, 선택적 research `data`; `design-methods.csv`; `{output_folder}`, 사용자명, 언어, 날짜. [E06]

**처리 단계:** 과제 정의 → 공감 → 문제 정의 → 발산적 ideation → 저충실도 prototype → 실제 사용자 test → 다음 iteration 계획. ideation 단계는 15~30개 아이디어와 2~3개 prototype 후보를 요구하고, test 단계는 5~7명 사용자 계획을 안내한다. [E06]

**출력/상태:** `design-thinking-{date}.md`의 challenge, empathy, POV/HMW, ideas, prototype, test, action item, metric 영역을 채운다. [E06]

## 2) Innovation Strategy

**입력:** 회사/사업, 탐색 계기, 현재 business model, 경계·제약, 성공 정의, 선택적 market context, `innovation-frameworks.csv`. [E06]

**처리 단계:** 전략 문맥 → 시장·경쟁 분석 → 현재 모델 분해 → disruption vector → 5~10개 기회 → 3개 전략 옵션 평가 → 권고 → 3단계 roadmap → 선행/후행 지표·decision gate·risk mitigation. [E06]

**출력/상태:** `innovation-strategy-{date}.md`에 시장, 모델, 기회, A/B/C 옵션, 추천, roadmap, metric/risk를 누적한다. [E06]

## 3) Problem Solving

**입력:** 문제와 증상·문맥, 이전 시도, 제약, 성공 기준, 선택적 problem brief, `solving-methods.csv`. [E06]

**처리 단계:** 문제 정제 → Is/Is Not 경계 → root cause → 힘·제약 분석 → 10~15개 해법 → 비교·추천 → 구현 계획 → monitoring/validation → 선택적 회고. [E06]

**출력/상태:** `problem-solution-{date}.md`에 원인 분석, 대안, 선택 근거, 책임·자원·일정, 검증 기준과 조정 trigger를 남긴다. [E06]

## 4) Storytelling

**입력:** 스토리 목적·대상·핵심 메시지·제약, 선택적 brand/context 파일, sidecar memory(있으면), `story-types.csv`. [E06]

**처리 단계:** 문맥 → framework 선택 → story element → 감정 곡선 → hook → 단독 초안/AI 초안/공동 작성 선택 → 길이별 variation → 활용 가이드 → 정제 → final output. [E06]

**출력/상태:** `story-{date}.md`에 framework, narrative, 감정 곡선, 짧은/중간/긴 버전, channel guide, feedback plan을 기록한다. 완료 문구와 저장을 지시하지만 실행 증거는 호스트 run에서만 확인 가능하다. [E06]

## 문서 사이트와 운영 흐름

`npm run docs:build`는 docs를 LLM용 텍스트와 Astro site로 빌드한다. `docs.yaml`은 `main`에 docs/website/build script 변경이 push되거나 수동 실행될 때 build artifact를 GitHub Pages로 배포하도록 정의한다. PR 품질 검사는 format, JavaScript/YAML lint, Markdown lint만 보장하며 workflow/agent 대화 결과·CSV 완전성·실제 Pages 배포 성공은 보장하지 않는다. [E03][E08][E09][E10]

