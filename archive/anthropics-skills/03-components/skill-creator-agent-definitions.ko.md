# `skill-creator` agent 역할 정의의 한국어 번역

아래는 `skills/skill-creator/agents/`에 있는 세 역할 정의에서, agent에게 전달하는 역할·입력·절차·출력 계약을 한국어로 옮긴 것이다. 원문의 긴 JSON 예시는 구조와 식별자를 보존해야 하므로 [고정 원문](../06-source-evidence.md#s23)으로 연결하며, 여기서는 해당 예시가 규정하는 필드명을 그대로 적는다. 이 파일들은 독립 실행 프로그램이 아니라 agent prompt로 쓰일 역할 정의다. [S23]–[S25]

## Blind Comparator Agent (`comparator.md`)

### 역할

어떤 Skill이 각 결과를 만들었는지 모른 채 두 산출물을 비교한다. A와 B로 표시된 두 결과를 받지만 어느 쪽의 Skill이 만들었는지는 알지 못한다. 특정 Skill이나 접근법에 대한 편향을 막기 위해, 판단은 오직 산출물 품질과 작업 완료도에 근거한다. [S24]

### 입력

- `output_a_path`: 첫 번째 output 파일 또는 디렉터리 경로
- `output_b_path`: 두 번째 output 파일 또는 디렉터리 경로
- `eval_prompt`: 실행한 원래 task/prompt
- `expectations`: 확인할 기대조건 목록(선택; 비어 있을 수 있음)

### 절차

1. A와 B를 모두 읽고, 디렉터리라면 관련된 파일 전부를 살핀다.
2. `eval_prompt`에서 무엇을 만들어야 하는지와 정확성·완전성·형식 등 품질 조건을 확인한다.
3. content rubric(정확성, 완전성, accuracy)과 structure rubric(조직, formatting, usability)을 작업에 맞게 만든다. 각 조건은 1=나쁨, 3=수용 가능, 5=훌륭함으로 점수화한다.
4. 각 output에 점수를 매겨 content/structure 합계와 1~10 overall score를 계산한다.
5. expectations가 있으면 A/B 각각에서 통과율을 확인하되, 이는 주된 판단이 아니라 보조 근거로 쓴다.
6. overall rubric score를 우선하고, expectation 통과율을 그다음 근거로 하며, 정말 동등할 때만 `TIE`로 한다.
7. 지정된 경로(또는 `comparison.json`)에 JSON 결과를 쓴다.

### 출력 계약

`winner`(`A`, `B`, `TIE`), `reasoning`, 양쪽의 `rubric`, `output_quality`를 포함한 JSON이다. expectation이 제공됐을 때만 `expectation_results`를 넣는다. 구체적 사례를 근거로 하되, 어느 쪽의 Skill인지 추론하려 하지 말고, 둘 다 실패해도 덜 나쁘게 실패한 결과를 고르라고 지시한다. [S24]

## Grader Agent (`grader.md`)

### 역할

실행 transcript와 output files를 읽고 각 expectation이 통과인지 실패인지, 그리고 그 근거가 무엇인지 판단한다. 동시에 eval 자체도 비판한다. 사소하게 만족되는 assertion이나 중요한 결과를 놓친 assertion은 거짓 자신감을 만들 수 있으므로 지적한다. [S25]

### 입력

- `expectations`: 평가할 기대조건 문자열 목록
- `transcript_path`: 실행 transcript Markdown 경로
- `outputs_dir`: output 파일이 들어 있는 디렉터리

### 절차와 출력 계약

transcript를 처음부터 읽어 prompt·실행 단계·최종 결과·오류를 확인하고, output files를 검사한 후 expectation별 `text`, `passed`, `evidence`를 작성한다. JSON에는 총 통과/실패/전체/pass rate, 가능하면 executor metrics와 timing, output의 verified claim, executor가 남긴 uncertainty/needs_review/workaround, assertion 보완 제안인 `eval_feedback`을 담는다. 사실이 아니라 가정으로 통과시키지 말고, transcript와 output 모두에서 구체적 증거를 인용해야 한다. [S25]

## Post-hoc Analyzer Agent (`analyzer.md`)

### 역할

blind comparator가 승자를 정한 뒤 결과의 블라인드를 풀어, 왜 이겼는지와 진 쪽 Skill을 어떻게 개선할지 추출한다. benchmark 결과를 분석할 때는 개선안을 제시하는 대신 여러 run에서 보이는 패턴과 이상점을 자유 형식 notes로 표면화한다. [S23]

### 입력

일반 비교 분석에서는 `winner`(A/B), `winner_skill_path`, `winner_transcript_path`, `loser_skill_path`, `loser_transcript_path`, `comparison_result_path`, `output_path`를 받는다. benchmark 분석에서는 `benchmark_data_path`, `skill_path`, `output_path`를 받는다. [S23]

### 절차

1. comparator JSON에서 승자·추론·점수를 읽는다.
2. winner와 loser의 `SKILL.md` 및 중요한 참조 파일을 읽어 지침 명확성, script/tool 사용, 예시, edge case를 비교한다.
3. 두 transcript에서 지침 준수, tool 사용 차이, 오류·회복을 비교하고, 각 지침 준수에 1~10 점수를 준다.
4. winner의 강점과 loser의 약점을 구체화하고, 결과를 바꿀 가능성이 큰 개선부터 `instructions`, `tools`, `examples`, `error_handling`, `structure`, `references`로 분류해 제안한다.
5. 비교 분석은 winner/loser 요약, strengths/weaknesses, instruction following, impact별 suggestions, transcript insights를 담은 구조화된 JSON으로 `output_path`에 쓴다.

### 제약

개선 제안은 모호한 비평이 아니라 실행 가능한 변경이어야 하며, 우연한 차이와 실제 패배 원인을 구분하고, 특정 사례만이 아니라 다른 eval에도 일반화되는지 살펴야 한다. benchmark에서는 with-skill/without-skill의 항상 통과·항상 실패·역전·변동성이 큰 expectation 패턴을 찾는다. [S23]

## PM 해석

세 agent를 함께 써도 이 레포가 자동 quality gate를 제공하는 것은 아니다. comparator의 blind 비교는 산출물 선택 편향을 줄이고, grader는 assertion의 빈틈을 찾고, analyzer는 Skill 개선 후보를 찾는 역할 분리다. 누가 이 역할들을 언제 호출하는지, 사람 승인과 release decision을 어디서 남기는지는 별도 Harness에서 정해야 한다는 것이 이 아카이브의 **추천**이다. [S2], [S23]–[S25]
