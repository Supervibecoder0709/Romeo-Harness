원문: agent-skills/codex/iterate-until-verified/SKILL.md  
고정 근거: [E08]

---
name: iterate-until-verified
description: 원래 요청을 보존하면서 상당한 작업에 prompt-agnostic 실행 및 검증 loop를 적용한다. 사용자가 work fan-out, subagent 또는 independent reviewer 사용, 완료될 때까지 loop, reference benchmark, 엄격한 critic, blind candidate 비교, 검증으로 기존 prompt 개선, 명시적 quality gate 통과까지의 지속을 요청할 때 사용한다.
---

# 검증될 때까지 반복

작업을 보존한다. 그 주변의 과정을 강화한다.

## 모드 선택

- **실행**: 아래 workflow로 원래 작업을 완료한다. 기본 모드다.
- **구성**: 사용자가 완성 작업물이 아니라 개선된 prompt를 요청하면 재사용 가능한 prompt wrapper를 반환한다. wrapper 안에서 원래 작업은 권위 있고 변경되지 않게 유지한다.

prompt 작성에서 실행으로 조용히 전환하지 않는다.

## 1. 원래 작업을 고정한다

다음을 추출한다.

- outcome과 deliverable
- audience와 use case
- 제공된 input과 reference
- constraint, tool, format, exclusion
- 허용된 action과 보호된 boundary
- 명시적 definition of done

이를 task contract로 취급한다. subject를 바꾸거나 requirement를 만들거나 constraint를 완화하거나 permission을 확장하거나 verification method가 deliverable이 되게 하지 않는다.

누락된 답이 작업을 실질적으로 바꾸고 안전하게 발견할 수 없을 때만 질문한다. 그렇지 않으면 합리적 가정을 밝히고 진행한다.

## 2. 야심을 gate로 바꾼다

perfect, best, professional, production-ready, AAA 같은 말을 관찰 가능한 check로 번역한다. 작업과 관련된 차원만 고른다.

- correctness와 factual accuracy
- 요청 대비 completeness
- craft, clarity, audience fit
- usability와 accessibility
- robustness, edge case, regression safety
- performance, security, compliance
- 제공된 benchmark에 대한 visual, editorial, technical fidelity

간결한 acceptance matrix를 만든다.

| Gate | Verification method | Pass condition | Evidence |
| --- | --- | --- | --- |
| 관련 quality dimension | test, inspection, comparison, read-back | 관찰 가능한 이진 조건 | command, source, screenshot, output, artifact |

모호한 점수보다 pass/fail 조건을 선호한다. wow 같은 강한 반응은 유용한 신호일 수 있지만 유일한 gate가 되면 안 된다.

## 3. 분해하고 배정한다

작업을 명확한 ownership, input, output, integration boundary를 가진 가장 작은 의미 단위 workstream으로 나눈다.

- 진정으로 독립적인 workstream만 fan out한다.
- race를 피하기 위해 결합된 edit는 한 owner에게 둔다.
- 각 worker에게 원래 task contract와 필요한 context만 준다.
- 모든 worker가 confidence claim이 아니라 artifact 또는 evidence를 반환하도록 한다.
- 한 integrator가 cross-workstream consistency와 regression을 책임지게 한다.

가능하고 허용되며 유용할 때 subagent 또는 delegated worker를 쓴다. 그렇지 않으면 같은 ownership boundary를 보존하면서 순차적으로 수행한다.

## 4. 만들기와 판정을 분리한다

구현자가 자기 작업의 유일한 승인자가 되게 하지 않는다.

verifier에게 다음을 준다.

- 원래 task contract
- acceptance matrix
- candidate artifact
- 관련 benchmark 또는 source material

verifier가 재현에 필요하지 않는 한 implementer의 rationale과 self-assessment는 주지 않는다. 먼저 failure를 찾고, evidence를 인용하고, 근거 없는 claim을 거절하고, gate별 verdict를 반환하도록 지시한다.

Blind comparison의 경우:

- 실용적이면 candidate를 anonymize하고 randomize한다.
- 같은 조건으로 동등한 대상을 비교한다.
- evaluator가 author나 candidate identity가 아니라 task와 rubric을 알고 있게 한다.
- 명백한 identity cue가 남았으면 blind라고 부르지 않는다.

## 5. 작업에 맞는 proof를 선택한다

가능한 가장 강한 verification surface를 사용한다.

- **Code**: focused test, typecheck, build, lint, security check, runtime behavior, regression test.
- **Visual work**: 관련 size의 rendered output, interaction check, accessibility check, 접근 가능한 reference와 side-by-side 비교.
- **Research/analysis**: primary source, 재현 가능한 calculation, citation check, contradiction search.
- **Writing**: factual check, brief coverage, audience fit, structure, representative reference에 대한 editorial pass.
- **Plan/decision**: constraint coverage, dependency check, failure scenario, feasibility, 명시적 tradeoff.
- **External action**: 정확한 target 확인 뒤 post-action read-back.

self-rating을 evidence로 바꾸지 않는다. benchmark, source, test result, screenshot, blind verdict를 발명하지 않는다.

## 6. Loop를 실행한다

다음을 반복한다.

1. candidate를 만들거나 개선한다.
2. 적용 가능한 모든 gate를 실행한다.
3. evidence와 함께 pass, fail, blocked를 기록한다.
4. 각 failure를 책임 workstream으로 보낸다.
5. evidence를 해결하는 최소 revision을 한다.
6. 실패 gate와 영향을 받은 regression gate를 다시 실행한다.
7. 검증된 작업만 통합한다.

필수 gate가 실패하고 안전하며 범위 내인 action으로 의미 있는 진전이 가능하면 계속한다. 같은 접근으로 반복 실패하면 소모하지 말고 접근을 바꾸거나 blocker를 보고한다.

## 7. 정직하게 멈춘다

다음일 때만 끝낸다.

- 모든 필수 gate가 pass
- 통합 결과가 여전히 원래 task를 충족
- 변경된 작업과 관련된 regression을 검사
- evidence가 최종 claim을 뒷받침
- 남은 unknown을 공개

필수 gate가 missing access, unavailable input, 새 authority, 불가능한 constraint에 의존하면 blocked로 끝낸다. 정확한 blocker와 최소 다음 action을 이름 붙인다. 성공 선언을 위해 gate를 약화하지 않는다.

## Compose mode template

개선된 prompt를 반환할 때 다음 형태를 사용한다.

~~~text
아래 authoritative task 주변에서 반복 실행 및 검증 workflow를 사용한다.

AUTHORITATIVE TASK
<subject, deliverable, constraint를 바꾸지 않고 사용자의 원래 task를 여기에 보존>

PROCESS
1. task contract를 추출하고 주관적 quality language를 관찰 가능한 acceptance gate로 바꾼다.
2. 독립 workstream을 분해하고 delegation이 유용하고 허용될 때 fan out한다.
3. 한 integrator가 consistency를 책임지게 한다.
4. implementer self-assessment는 보지 않고 task, rubric, candidate, reference를 보는 independent verifier를 배정한다.
5. task에 맞는 evidence로 verify한다. 실제 비교 가능한 benchmark가 있을 때 anonymized side-by-side comparison을 사용한다.
6. 실패 gate를 책임 workstream으로 보내 revision하고 영향을 받은 regression을 재확인한다.
7. 모든 required gate가 pass하거나 concrete blocker가 증명될 때까지 끝내지 않는다.

FINAL RESPONSE
deliverable, 간결한 gate별 evidence summary, 아직 검증되지 않은 것을 반환한다. 실행하지 않은 check를 주장하지 않는다.
~~~

과정은 task에 맞춘다. 다른 prompt의 domain-specific tool, benchmark, quality claim을 해당되지 않으면 복사하지 않는다.

## 완료 점검

- 원래 task가 여전히 권위 있다.
- 주관적 야심이 관찰 가능한 gate가 됐다.
- 독립 작업을 race 없이 분리했다.
- 만들기와 판정이 다른 role에 배정됐다.
- benchmark가 실제이고 비교 가능하며 정직하게 label됐다.
- failure가 revision을 이끌었다.
- 최종 claim이 수집한 evidence와 맞는다.
