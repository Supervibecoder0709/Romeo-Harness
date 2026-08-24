# 실행·검증 구성요소

이 문서는 Skill 정의 파일은 아니지만, 선택된 Skill의 본문이 지목하고 고정 트리에서 실제 파일로 확인한 실행 핵심을 설명한다. **사실**은 코드 또는 지침의 관찰 내용이고, 실행해 보지 않은 결과는 미검증으로 남긴다.

## `skill-creator`: 정의 품질과 trigger 평가

- **`scripts/quick_validate.py` (확인됨):** 인자로 받은 skill 디렉터리에서 `SKILL.md` 존재 여부, YAML frontmatter의 형식·파싱, 허용 키, 필수 `name`/`description`, kebab-case 이름과 길이, description의 꺾쇠괄호·길이, 선택 `compatibility`를 검사하고 성공/실패 exit code를 낸다. 이 도구는 `license`를 허용 키로 보지만 라이선스 전문 또는 본문 지침의 품질을 평가하지는 않는다. [S20]
- **`scripts/run_eval.py` (확인됨):** 임시 `.claude/commands/<unique>.md`를 만들고 `claude -p`를 `stream-json`, partial messages와 함께 실행해 Skill/Read 도구 호출에서 해당 이름이 등장하는지를 trigger로 판정한다. 기본값은 query당 3회, query별 timeout 30초, 임계치 0.5이며, process pool에서 병렬 실행한다. 끝나면 command file을 삭제하려고 한다. 따라서 실제 Claude CLI, 모델, 로컬 `.claude` 쓰기 권한과 사용량이 필요한 **실행형 평가**다. [S21]
- **`scripts/run_loop.py` (확인됨):** eval과 description 개선 루프를 결합하고, holdout 비율이 양수이면 `should_trigger`별로 train/test를 나누도록 구현한다. 이론상 과적합을 막기 위한 구조이나, 이 아카이브에서 실행·결과·품질은 검증하지 않았다. [S22]
- **agent 정의 (확인됨):** `comparator`는 A/B 산출물의 출처를 모른 채 rubric으로 승자를 고르고, `grader`는 transcript·출력에 대한 expectation 통과 여부와 eval 자체의 약점을 판단하며, `analyzer`는 blind comparison 뒤 결과를 공개해 승패 원인을 개선 제안으로 만든다. 이들은 실행 스케줄러나 접근 제어 코드가 아니라 자연어 역할 계약이다. [S23]–[S25]

## `web-artifacts-builder`: 준비와 단일 HTML 번들

- **`scripts/init-artifact.sh` (확인됨):** Node.js major version을 읽어 18 미만이면 실패한다. `pnpm`이 없으면 `npm install -g pnpm`을 실행하고, Vite React TypeScript 프로젝트 생성, 패키지 설치, Tailwind 설정, shadcn 구성요소 tarball 추출 등을 수행한다. 즉 이 스크립트는 생성 대상 디렉터리와 전역 pnpm 설치를 변경하고 네트워크 패키지 설치를 요청할 수 있어, 안전한 읽기 전용 분석과는 다른 권한 경계다. [S26]
- **`scripts/bundle-artifact.sh` (확인됨):** 현재 디렉터리에 `package.json`·`index.html`이 있어야 하며, Parcel·resolver·`html-inline`을 dev dependency로 추가하고, 이전 `dist`와 `bundle.html`을 삭제한 다음 `bundle.html`을 만든다. 성공 메시지와 파일 크기를 출력한다. 출력 파일 존재·브라우저 렌더링은 개별 실행에서 별도 확인해야 한다. [S27]

## `webapp-testing`: 로컬 서버 수명주기

- **`scripts/with_server.py` (확인됨):** 하나 이상 `--server` 명령과 같은 수의 `--port`를 받아 shell subprocess로 서버를 시작하고, localhost TCP 연결을 0.5초 간격으로 최대 기본 30초 기다린다. 모두 준비되면 지정한 테스트 명령을 실행하고, `finally`에서 terminate 후 5초 내 종료하지 않으면 kill한다. `shell=True`이므로 server 문자열은 신뢰한 프로젝트 명령만 전달해야 한다. 성공 여부는 테스트 command의 반환 코드로 전달되지만 테스트의 의미·coverage는 이 helper가 보장하지 않는다. [S28]

## `algorithmic-art`: 재현 가능한 생성 템플릿

- **`templates/generator_template.js` (확인됨):** 조정 가능한 `params` 객체와 `seed`, `randomSeed`/`noiseSeed` 초기화, p5.js lifecycle, parameter update·regenerate·PNG export의 구조를 제시한다. 템플릿 본문은 특정 예술 결과를 강제하지 않으며, seed를 같은 값으로 둘 때 p5.js 난수·noise 호출이 결정적이 되도록 안내한다. [S29]

## 기타 구현 자산: 존재·범위만 확인

- `pdf`에는 채울 수 있는 양식의 field 정보·구조 추출, field 채움, 주석 기반 채움, 이미지 변환·검사 scripts가 있다. `pdf/SKILL.md`는 PDF 읽기, OCR, 생성, form fill을 사용 범위로 지시한다. 개별 스크립트의 입력 포맷·출력 정확도는 이 아카이브에서 실행하지 않아 미검증이다. [S14], [S2]
- `docx`, `pptx`, `xlsx`에는 Office validation helper와 validator 패키지가 있고, `xlsx`에는 `recalc.py`, `pptx`에는 slide 추가·정리·thumbnail script가 있다. `pptx/SKILL.md`는 QA를 required라고 표시하고, `xlsx/SKILL.md`는 수식이 있으면 재계산을 mandatory로 표시한다. 그러나 범용 테스트 스위트나 실행 결과는 확인되지 않았다. [S15], [S19], [S2]
- `mcp-builder`에는 MCP 연결·평가 scripts, Python/Node 구현 reference가 있다. Skill 본문은 조사·계획→구현→검토·테스트→evaluation 생성을 4단계로 둔다. 외부 API의 인증·권한·실제 호출을 이 저장소가 일괄 승인하거나 보관한다는 근거는 없다. [S13], [S2]
- `slack-gif-creator`에는 GIF builder, validator, easing, frame composer가 있다. `GIFBuilder.save()`는 frame 유무를 확인하고 색상 수·중복 frame·emoji 최적화 옵션에 따라 GIF를 쓰고 경로·크기·frame 수 등의 정보를 반환한다. Slack 실제 업로드 성공과 플랫폼 제한 충족은 여기서 확인되지 않는다. [S16], [S30]
