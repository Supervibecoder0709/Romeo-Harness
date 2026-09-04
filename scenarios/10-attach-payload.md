# 시나리오 10 — 부착이 무엇을 놓고 무엇을 덮는가

하네스를 **자기 저장소가 아닌 저장소**에 손으로 붙이는 절차다. 대상은 `My-Automated-Worker/instagram-dm-sender` 이고,
이 런북이 고정하는 것은 「부착」이라는 낱말이 아니라 **파일 목록과 종료 코드**다.

이 런북이 필요한 이유는 부착 검증이 **부재를 통과로 읽었기** 때문이다. 아무것도 부착하지 않은 빈 저장소에
`.harness/compiled.yaml`(`outputs: []`)과 빈 `THIRD_PARTY_NOTICES.md` 만 놓으면
`bin/romeo doctor --strict --scope repository` 가 **exit 0** 을 낸다(2026-09-04 실측) — 산출물 0개가 목록 0개와 일치하고,
vendor import 0건이 0건과 일치하고, 충돌 fixture 0종에서 충돌이 0건이기 때문이다. 세 검사가 전부 참인데
그 저장소에는 하네스가 없다. 그래서 부착 여부는 `doctor` 가 아니라 **이 문서의 「놓는 것」 목록**이 판정하고,
`tests/test_attach_runbook.py` 가 그 목록을 이 파일에서 읽어 매번 재현한다.

부착을 **자동화하지 않는다**. 손으로 밟는 것이 이 단위의 방법이고, 여기서 나온 것이 `attach` 명령(M5)의 요구사항이 된다.

## 부착 전 확인

하나라도 어긋나면 부착을 시작하지 않는다. 되돌리기가 `git` 하나에 걸려 있으므로, 부착 전 상태가 깨끗한 것이 복구의 전제다.

| # | 확인 | 명령 | 통과 조건 |
| --- | --- | --- | --- |
| 1 | 대상이 clean 인가 | `git -C <대상> status --porcelain` | 출력이 비어 있다. 그러면 부착분이 `git status` 만으로 갈린다 |
| 2 | 부착 전 지침 파일을 기록했는가 | `wc -l <대상>/CLAUDE.md` · `shasum -a 256 <대상>/CLAUDE.md` | 줄 수와 해시를 적어 둔다 — 「덮는 것과 보존」의 대조 기준이다 (실측 2026-09-04: **106줄**) |
| 3 | 지워질 권한 규칙을 기록했는가 | `cat <대상>/.claude/settings.json` | `permissions.deny` 의 값을 **글자 그대로** 아래 「덮는 것과 보존」에 옮겨 적는다 |
| 4 | 하네스 리비전을 적었는가 | `git -C <하네스> rev-parse HEAD` | 부착분이 어느 리비전의 복제인지 남는다 — 드리프트가 시작되는 지점이다 |

대상 저장소에 이미 다른 하네스(예: BMad)가 붙어 있어도 제거하지 않는다. 공존이 관측 대상이다.

## 놓는 것

**목록의 문법.** 이 절에서 `- ` 로 시작하고 백틱으로 감싼 경로가 첫 토큰인 줄만 필수 경로로 읽는다.
`tests/test_attach_runbook.py` 의 `required_paths()` 가 이 파일을 읽어 그 목록을 만들고,
`check()` 가 주어진 루트와 대조한다. **이 목록을 고치면 검사가 대조하는 것이 함께 바뀐다** — 항목을 지우면
그 항목은 조용히 건너뛰어지는 것이 아니라 요구에서 사라지고, 항목을 더하면 그 자리에서 막힌다.
검사가 매번 목록을 바꿔 넣어 그 사실을 재확인한다.

앞의 여섯은 **손으로 복사하는 하네스 소스 트리**다. `romeo compile` 의 `--root` 가 읽는 곳과 쓰는 곳을 둘 다 정하므로
(`romeo/compile.py` 의 `plan_outputs`), 대상 저장소 안에 이것들이 없으면 컴파일은 산출물 0개로 **성공**한다.

- `core/` — 코어 규칙·정책표·역할 계약·워크플로 원본
- `adapters/` — 런타임 매핑(지침 파일 경로·스킬 경로·권한 설정 경로)
- `vendor/` — 채택된 부품 원문. `provenance/imports.yaml` 이 `accepted` · `verbatim` 으로 표시한 것만 투영된다
- `provenance/` — 부품 출처·라이선스. `THIRD_PARTY_NOTICES.md` 의 원본이다
- `skills/repo-archive/` — 어댑터의 `local_skills` 원본
- `.harness/bindings.yaml` — 역할↔런타임 바인딩·권한 상한 정본

뒤의 여덟은 **`romeo compile` 과 `romeo notices` 가 만드는 산출물**이다. 손으로 만들지 않는다.

- `.harness/compiled.yaml` — 무엇이 하네스 소유인지 적는 목록. 이것이 없으면 되돌리기가 성립하지 않는다
- `CLAUDE.md` — managed block 주입 (마커 밖은 보존한다)
- `AGENTS.md` — managed block 주입
- `.claude/settings.json` — `permissions.ask` · `permissions.deny` **대체** (아래 절이 그 결과를 적는다)
- `.claude/agents/` — 역할 계약의 런타임 투영 (`implementer.md` · `reviewer.md`)
- `.claude/skills/` — 워크플로 4종 + vendor 원문 7종 + `repo-archive`
- `.agents/skills/` — 같은 것의 다른 런타임 투영
- `THIRD_PARTY_NOTICES.md` — `bin/romeo notices` 산출물

놓는 순서는 소스 트리 여섯 → `bin/romeo compile --root <대상>` → `bin/romeo notices --root <대상>` 이다.
`bin/` 과 `romeo/`(파이썬 패키지)는 **놓지 않는다** — 명령은 하네스 저장소에서 `--root <대상>` 으로 실행한다.
그래서 대상 저장소만으로는 라우터를 돌릴 수 없다. 그 사실이 M5 `attach` 가 답해야 할 것이다(`docs/planning/open-questions.md` Q-54).

## 덮는 것과 보존

| 대상 | 덮는 방식 | 보존되는 것 | 지워지는 것 |
| --- | --- | --- | --- |
| `CLAUDE.md` · `AGENTS.md` | `<!-- romeo:managed start ... -->` ~ `end` 마커 사이만 갈아 끼운다 | 마커 **밖**의 모든 줄. 대상의 부착 전 **106줄**이 블록 앞에 그대로 남는다 (AC-5) | 없음 |
| `.claude/settings.json` | JSON 이라 managed 마커를 넣을 수 없다 — `permissions.ask` 와 `permissions.deny` 를 **통째로 대체**한다 (`romeo/compile.py` 의 `_render_settings`) | `permissions` 밖의 키와 `permissions` 안의 다른 키. 대상의 `additionalDirectories: ["~/.coupang-auto"]` 는 남는다 | 아래 두 줄 |

부착이 대상의 `.claude/settings.json` `permissions.deny` 에서 **지우는 실제 값**(2026-09-04 실측):

```
Write(~/.coupang-auto/**)
Edit(~/.coupang-auto/**)
```

**복원하지 않는다.** 사용자가 「기존 프로젝트 규칙은 다 무시하고 부착을 우선한다」로 확정했다(2026-09-04).
여기 적는 이유는 복원을 위해서가 아니라, **병합이 아니라 대체라는 것**이 M5 `attach` 가 반드시 다뤄야 할 실측이기 때문이다.
자동화를 먼저 만들었다면 이 두 줄은 아무도 모르는 채 사라졌을 것이다.

## 검증

부착 여부는 아래 순서로 판정한다. **1번이 판정이고, 2~4번은 그 위에서만 의미가 있다.**

| # | 명령 | 무엇을 판정하나 |
| --- | --- | --- |
| 1 | `python3 -m unittest tests.test_attach_runbook` | 이 문서의 「놓는 것」 목록이 대상 루트에 **실제로 있는가**. 부재를 통과로 읽지 않는다 |
| 2 | `bin/romeo compile --check --root <대상>` | 산출물이 소스 트리와 최신인가 |
| 3 | `bin/romeo notices --check --root <대상>` | 제3자 고지가 `provenance/imports.yaml` 과 일치하는가 |
| 4 | `bin/romeo doctor --strict --scope repository --root <대상>` | 컴파일 산출물·vendor 원문·고지·충돌 fixture |

**4번을 단독으로 쓰지 않는다.** 옵션 없이 쓴 `bin/romeo doctor` 는 항상 exit 0 이고(Q-21),
`--strict --scope repository` 를 붙여도 **아무것도 부착하지 않은 저장소가 통과한다**(2026-09-04 실측 · Q-53).
거꾸로 **완전히 부착한 대상 저장소는 exit 1 이었다** — 부착 상태 3건은 전부 일치인데, 대상이 원래 갖고 있던 심링크 스킬 8개가
「Windows 에서 깨진다」로 세어졌기 때문이다(2026-09-04 실측 · Q-55). 4번의 종료 코드는 부착 여부를 말하지 않는다.
1번이 그 구멍을 막는 자리다.

## 되돌리기

부착 전 `git status` 가 clean 이었으므로 두 명령이 완전한 복구다.

```
git -C <대상> checkout -- .claude/settings.json CLAUDE.md
git -C <대상> clean -fd .agents .claude/agents .claude/skills .harness adapters core provenance vendor skills/repo-archive AGENTS.md THIRD_PARTY_NOTICES.md
```

첫 줄이 **덮인 것**(추적되던 두 파일)을 되돌리고, 둘째 줄이 **놓은 것**(추적되지 않던 파일)을 지운다.
두 목록은 위 「놓는 것」·「덮는 것과 보존」과 같은 것을 가리켜야 한다 — 어긋나면 부착분이 남거나 대상의 파일이 지워진다.

`git clean` 은 **되돌릴 수 없다**. 대상이 clean 이라는 「부착 전 확인」 1번을 건너뛰면 이 명령이
사용자의 미커밋 작업을 지운다. 그래서 확인 1번이 절차의 첫 줄에 있다(K-66).

하네스 저장소 쪽은 `git revert <구현 커밋>` 이다. 운영 상태·외부 상태·비용은 이 절차가 건드리지 않는다.
