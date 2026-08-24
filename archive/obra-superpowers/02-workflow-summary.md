# 워크플로우 요약

## 무엇을 하는가

**확인된 사실**: Superpowers는 coding agent에 계획·TDD·디버깅·검토·통합 절차를 부여하는 Markdown skill 라이브러리와 harness adapter 모음이다. 중앙 SaaS나 공용 데이터베이스가 업무를 대신 실행하는 구조가 아니라, 설치된 harness가 bootstrap과 skill을 model 문맥에 제공하고 agent가 그 지침을 따라 작업하는 구조다. [E03](06-source-evidence.md#e03) [E05](06-source-evidence.md#e05) [E10](06-source-evidence.md#e10)

## 입력

1. 사용자의 자연어 요청, 기존 코드/문서, 직접 지시 파일.
2. 설치된 harness의 session-start·config·context event 또는 native skill discovery.
3. 구현 단계에서는 승인된 spec, plan, repository 상태, test output.
4. 선택적 visual companion에서는 agent가 쓴 HTML 화면 파일과 브라우저가 보낸 choice event.

## 처리 단계

```text
Harness 설치/시작
  → using-superpowers bootstrap 로드 또는 skill 경로 등록
  → 현재 요청에 맞는 skill을 먼저 확인
  → 아이디어라면 brainstorming: spike / bounded / architectural 분류
  → 사람의 설계 승인
  → (architectural) spec → writing-plans → 실행 방식 선택
  → isolated worktree + baseline test
  → TDD로 task 구현, task별 독립 review
  → fresh verification
  → 사람이 merge / PR / branch 보존 중 선택
```

- `using-superpowers`는 응답·파일 탐색·질문보다 먼저 관련 skill을 호출하라고 규정한다. [E13](06-source-evidence.md#e13)
- `brainstorming`은 규모가 작아도 구현 전 설계와 명시적 승인을 hard gate로 둔다. spike는 추천 보고로 끝나고, bounded는 짧은 채팅 설계 승인 후 구현하며, architectural은 spec·plan까지 만든다. [E14](06-source-evidence.md#e14)
- 계획이 있으면 `writing-plans`가 task별 정확한 파일·인터페이스·실패 test·통과 test·commit을 포함하도록 요구한다. [E15](06-source-evidence.md#e15)
- SDD는 task마다 fresh implementer, spec/quality review, 최대 5회 fix/re-review loop, 마지막 whole-branch review를 지시한다. 이 전부는 skill instruction이지 Superpowers 서버가 강제하는 트랜잭션은 아니다. [E16](06-source-evidence.md#e16) [E17](06-source-evidence.md#e17)

## 출력과 상태

| 층 | 생성·변경되는 것 | 확인된 위치/경계 |
|---|---|---|
| 지식 산출물 | chat design, spec, implementation plan | 기본 경로는 `docs/superpowers/specs/`, `docs/superpowers/plans/`; 사용자 선호가 우선 [E14](06-source-evidence.md#e14) [E15](06-source-evidence.md#e15) |
| 코드 산출물 | worktree의 코드·tests·commits | 실제 write는 사용 중인 coding agent/harness가 수행; Superpowers source 자체가 사용자의 프로젝트를 직접 수정하지는 않음 |
| 실행 복구 기록 | plan-scoped SDD ledger, brief, report, review package | `<repo>/.superpowers/sdd/<plan-basename>/`; git-ignored scratch라 `git clean -fdx`로 사라질 수 있고 commits가 회복 근거다. [E16](06-source-evidence.md#e16) |
| visual companion | session `content/`, `state/`, events, server info/log/token | 기본 `/tmp` 또는 `<project>/.superpowers/brainstorm/`; 선택적 local Node server. [E25](06-source-evidence.md#e25) [E27](06-source-evidence.md#e27) |
| 배포/통합 | merge, push, PR, branch/worktree 보존·삭제 | 선택권은 사람에게 있으며, 외부 side effect다. [E21](06-source-evidence.md#e21) |

## 실패와 재시도

- bootstrap을 읽지 못하면 OpenCode는 `null`, Pi는 예외를 잡아 `null`을 반환한다. 이는 해당 adapter의 주입을 건너뛰는 경로이며 사용자에게 명시적으로 오류를 알리는 공통 보장은 아니다. [E10](06-source-evidence.md#e10) [E11](06-source-evidence.md#e11)
- SDD implementer 상태는 `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, `BLOCKED`다. context 보강, 상위 모델, task 분할, plan ruling 후 re-dispatch를 지시하고, 같은 조건의 무의미한 재시도는 금지한다. [E17](06-source-evidence.md#e17)
- review finding은 fix와 scoped re-review를 짝으로 최대 5회 반복한다. 이후에도 남으면 ledger에 ruling을 남기고 구조적으로 중요한 결함만 다음 task로 전달한다. [E17](06-source-evidence.md#e17)
- visual server는 인증 안 된 HTTP/WS를 거부하고, owner process 종료 또는 idle timeout이면 socket을 닫고 종료한다. stop script는 PID와 instance id가 일치할 때만 signal한다. [E26](06-source-evidence.md#e26) [E27](06-source-evidence.md#e27) [E28](06-source-evidence.md#e28)

## 관찰 가능한 완료 증거

완료라고 부르려면 최소한 다음을 구분해야 한다.

1. **계획 승인**: chat 또는 spec review에 사람의 명시적 승인 기록이 있는가.
2. **구현**: plan ledger와 Git diff/commit이 task 산출물을 보여 주는가.
3. **검토**: task review와 final review의 verdict가 파일로 남았는가.
4. **검증**: 지금의 tree에서 전체 test command를 실행했고 exit code·실패 수를 읽었는가. 이전 green run이나 agent self-report만으로는 부족하다. [E19](06-source-evidence.md#e19)
5. **외부 결과**: merge/push/PR은 실제 URL, remote state, merged tree를 readback한 뒤에만 완료로 표시해야 한다. 이 마지막 항목은 source가 지시하는 방향이고, 이 아카이브에서는 실제 실행하지 않아 **미확인**이다. [E21](06-source-evidence.md#e21)
