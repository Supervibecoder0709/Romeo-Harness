---
name: od-contribute
description: OpenDesign(nexu-io/open-design)을 위한 원클릭 기여 흐름 — 비개발자도 사용할 수 있습니다. 네 가지 카드 중 하나(Skill 또는 Design System 올리기, 문서 번역, 오타 수정/블로그 작성, 버그 신고)를 고르면 agent가 검증하고 PR(또는 issue)을 엽니다. Trigger words contribute to open design, ship my OD skill, ship my OD design system, translate OD docs, report an OD bug, od-contribute.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - AskUserQuestion
  - TaskCreate
  - TaskUpdate
  - WebFetch
---

# od-contribute — OpenDesign 첫 기여 흐름

`nexu-io/open-design`에 고정됩니다. issue가 아니라 **기여 유형**으로 분기합니다. dev loop를 유형별 no-code validator로 대체합니다. 코딩 배경이 전혀 없는 product user도 실제 PR을 올릴 수 있게 설계됐습니다.

## 언어

모든 user-facing message에서 사용자의 언어를 따릅니다. `AskUserQuestion` label/description, status update, error explanation을 포함합니다. 첫 메시지에서 언어를 감지하고 확실하지 않으면 English를 기본으로 합니다.

생성 artifact(PR title, commit message, PR/issue body file, branch name)는 사용자의 chat 언어와 관계없이 반드시 English여야 합니다. GitHub convention, maintainer review, search가 English를 전제합니다. `templates/` 아래 template은 이미 English이므로 render할 때도 유지합니다.

script는 `scripts/` 아래에 있습니다. 어느 script에서나 shared helper를 source합니다.

```bash
source "$(dirname "$0")/config.sh"
```

아래의 `SKILL_DIR`은 이 `SKILL.md`가 있는 directory를 뜻합니다.

---

## Step 1 — Prereq check (항상 먼저)

```bash
bash "$SKILL_DIR/scripts/check-prereqs.sh"
```

- Exit 0: stdout에서 `GH_USER=<login>`을 기록합니다. 기본 `TARGET_FORK="${GH_USER}/open-design"`입니다.
- Exit 2: 출력된 install/auth hint를 **그대로** 보여 주고 중단합니다. token workaround를 시도하지 않습니다.

`gh repo view "$TARGET_FORK"`가 실패하면, `gh repo fork nexu-io/open-design --clone=false`로 지금 fork할지 사용자에게 `AskUserQuestion` 한 번으로 묻습니다. 기본값은 yes입니다.

## Step 2 — 기여 유형 선택

`AskUserQuestion` 하나만 사용합니다(header: "Contribution", multiSelect: false). 네 option의 label/description은 사용자의 chat 언어로 번역하되 branch routing은 바꾸지 않습니다.

1. **🎨 Ship something I made with OD** — _OD로 만든 Skill, Design System, HyperFrame, template을 upstream에 기여하고 싶음_ → branch `3a`
2. **🌍 Translate OD docs** — _README / QUICKSTART / CONTRIBUTING을 새 언어로 번역_ → branch `3b`
3. **📝 Fix docs / write a blog / fix a typo** — _오타, 죽은 링크, use-case 글_ → branch `3c`
4. **🐛 Report a bug** — _무언가 고장 났고, 품질 높은 issue로 만들고 싶음_ → branch `3d` (issue path, PR 없음)

아래 branch는 각각 self-contained입니다. Step 7–8(preview + push)은 `3a`/`3b`/`3c`가 공유합니다. `3d`는 이를 모두 건너뜁니다.

---

### Step 3a — OD product submission (Skill / Design System)

**3a.1** 사용자에게 “올리고 싶은 artifact의 local path는 무엇인가요?”를 묻습니다(single free-text, 사용자의 chat 언어로 번역). 흔한 경우는 folder path(Skill) 또는 단일 `DESIGN.md` file(Design System)입니다.

**3a.2** 유형을 sniff합니다.

```bash
# Skill: frontmatter가 있는 SKILL.md를 포함한 folder.
# Design System: DESIGN.md anatomy에 맞는 file.
```

모호하면 사용자에게 확인을 요청합니다.

**3a.3** setup을 실행합니다.

```bash
bash "$SKILL_DIR/scripts/setup-workspace.sh" skill <slug>
# 또는
bash "$SKILL_DIR/scripts/setup-workspace.sh" design-system <slug>
```

`<slug>`는 Skill `name` frontmatter field 또는 brand name의 `od::slugify`입니다. stdout에서 `WORKDIR`을 기록합니다.

**3a.4** artifact를 workspace의 올바른 target directory로 복사합니다.

- Skill → `$WORKDIR/skills/<slug>/`
- Design System → `$WORKDIR/design-systems/<brand-slug>/DESIGN.md` (+ 같은 folder의 sibling asset)

**3a.5** 검증합니다.

```bash
bash "$SKILL_DIR/scripts/validate-skill-submission.sh" "$WORKDIR/skills/<slug>"
# 또는 reference DESIGN.md file 1–2개를 전달해
bash "$SKILL_DIR/scripts/validate-design-system.sh" \
  "$WORKDIR/design-systems/<slug>/DESIGN.md" \
  --reference "$WORKDIR/design-systems/airbnb/DESIGN.md" \
  --reference "$WORKDIR/design-systems/apple/DESIGN.md"
```

검증이 실패하면 FAIL line을 그대로 보여 주고, 사용자가 고치게 한 뒤 재시도합니다. **실패한 artifact를 절대 push하지 않습니다.**

**3a.6** `AskUserQuestion`으로 짧은 질문 3개를 합니다(label은 사용자의 chat 언어로 번역).

- “PR에서 어떤 이름으로 credit을 표기할까요?” — free-text
- “이 Skill / Design System을 설명하는 한 줄 pitch는?” — free-text
- “screenshot path(선택 사항)는?” — free-text

**3a.7** `templates/PR-BODY-skill.md`(또는 `PR-BODY-design-system.md`)를 다음 치환값으로 render합니다.

- `{{SKILL_NAME}}`, `{{SKILL_SLUG}}` (또는 `{{BRAND_NAME}}`, `{{BRAND_SLUG}}`)
- `{{PITCH}}` (한 줄 설명)
- `{{MOTIVATION}}` (free-text — agent는 skill body에서 draft를 제안할 수 있으나 사용자가 확인)
- `{{TRY_PROMPT}}` (권장 시험 prompt — agent가 default를 제안하고 사용자가 확인)
- `{{SCREENSHOT_BLOCK}}` (screenshot path가 있으면 Markdown image block, 없으면 비움)
- `$OD_DISCORD_INVITE`의 `{{DISCORD_INVITE}}`

`$WORKDIR/.od-contrib/PR-BODY.md`에 씁니다.

→ **Step 7**로 이동합니다.

---

### Step 3b — i18n 번역

**3b.1** workspace를 setup합니다(doc/lang을 알면 slug는 `translate-<doc>-<lang>`, 아니면 `translate`).

```bash
bash "$SKILL_DIR/scripts/setup-workspace.sh" i18n translate
# WORKDIR을 기록
```

**3b.2** gap을 찾습니다.

```bash
bash "$SKILL_DIR/scripts/discover-i18n-gaps.sh" "$WORKDIR" > /tmp/od-i18n-gaps.json
```

각 line은 JSON입니다. 다음 우선순위로 정렬합니다.

- 먼저 `status: "missing"`(누락 언어가 가장 높은 leverage)
- 그다음 `status: "stale"`, `english_commits_since_translation` 내림차순
- README family를 QUICKSTART보다, QUICKSTART를 CONTRIBUTING보다 먼저

**3b.3** 상위 gap 3–4개를 `AskUserQuestion`으로 제시합니다(header: "Translation target"). option label 예: `README → 한국어 (Korean)` / `QUICKSTART (zh-CN) refresh — 12 commits behind`. header는 사용자의 chat 언어로 번역하되, 언어 이름은 native script로 descriptive하게 유지합니다.

**3b.4** 사용자가 고르면 branch 이름을 구체적으로 바꿉니다.

```bash
git -C "$WORKDIR" branch -m "od-contrib/i18n/<doc>-<lang>-<date>"
```

(또는 사용자가 더 일찍 확인했다면 Step 3b.1에서 slug를 미리 설정합니다.)

**3b.5** 번역합니다. English source를 읽고 **structure-preserving**으로 번역합니다.

- code block: 번역하지 않음
- brand / product name: 번역하지 않음
- inline code의 filename: 번역하지 않음
- image / link target: 번역하지 않음. linked doc의 localized version이 있으면 localized file로 link를 바꿈
- heading: 번역하되 heading depth를 동일하게 유지
- table: cell text만 번역하고 alignment / pipe 유지

결과를 `$WORKDIR/<TRANSLATED_PATH>`(예: `QUICKSTART.es.md`)에 씁니다. visual sanity-check를 위해 English source와 unified diff를 보여 줍니다(line-count delta가 ±15% 안이면 건강한 신호입니다).

**3b.6** 번역 파일을 English source에 맞춰 검증합니다. `--reference`는 English source에 이미 깨져 있던 relative ref를 무시하도록 합니다. OD 문서는 website route slug(예: `skills/blog-post/`)를 file이 아닌 곳에 link하는 경우가 흔하므로 structure-preserving translation이 pre-existing dead ref 때문에 실패하지 않게 합니다.

```bash
bash "$SKILL_DIR/scripts/validate-markdown.sh" \
  "$WORKDIR/<TRANSLATED_PATH>" \
  --reference "$WORKDIR/<ENGLISH_PATH>"
```

FAIL이면 그대로 보여 주고 고친 뒤 재시도합니다.

**3b.7** `templates/PR-BODY-i18n.md`를 `{{DOC_NAME}}`, `{{LANG_DISPLAY_NAME}}`, `{{LANG_CODE}}`, `{{TRANSLATED_PATH}}`, `{{ENGLISH_PATH}}`, `{{STATUS}}`, `{{TRANSLATION_NOTES}}`(agent의 한 paragraph: 어려웠던 점, 유지한 untranslated term 등), `{{DISCORD_INVITE}}`로 render합니다.

→ **Step 7**로 이동합니다.

---

### Step 3c — Docs / blog / typo

**3c.1** workspace를 setup합니다(slug `docs`).

```bash
bash "$SKILL_DIR/scripts/setup-workspace.sh" docs <slug>
```

**3c.2** 사용자에게 `AskUserQuestion` 한 번으로 다음을 묻습니다.

1. **Auto-discover small fixes** (`discover-doc-gaps`를 실행하고 하나 선택)
2. **I have a specific fix in mind** (free-text)
3. **I want to write a blog / case study** (free-text — use case가 무엇인가?)

**3c.3 (Auto-discover branch)** 다음을 실행합니다.

```bash
bash "$SKILL_DIR/scripts/discover-doc-gaps.sh" "$WORKDIR" > /tmp/od-doc-gaps.json
```

`kind`(typo / deadlink / todo)별로 묶어 최대 6개 후보를 `AskUserQuestion`으로 보여 줍니다. 선택 후 code에서 수정합니다(typo: 단어 교체, deadlink: 새 URL을 사용자에게 요청, todo: 제대로 된 task이므로 사용자가 누락 prose를 작성하게 함).

**3c.4 (Specific-fix branch)** file을 읽어 사용자가 설명한 변경을 적용하고 diff로 확인합니다.

**3c.5 (Blog branch)** 먼저 OD에 blog directory가 있는지 확인합니다.

```bash
ls "$WORKDIR/docs" 2>/dev/null
```

`docs/blog/` 또는 비슷한 경로가 있으면 새 post를 그곳에 둡니다. 없으면 사용자에게 위치를 묻고 기본값은 `docs/<slug>.md`입니다. outline을 만들고 사용자가 user-specific bit(use case, screenshot, 사용한 prompt, rendered output)를 채우면 agent가 final Markdown으로 엮습니다.

**3c.6** 변경/추가된 모든 file을 검증합니다. repo에 이미 있던 file(typo/dead-link/doc edit)은 `--reference`로 HEAD version을 전달해 사용자가 **도입한** relative ref만 실패시키고 기존 route slug는 실패시키지 않습니다.

```bash
# 기존 file을 수정하는 경우:
git -C "$WORKDIR" show "HEAD:<path>" > "/tmp/od-contrib-orig-<basename>" 2>/dev/null
bash "$SKILL_DIR/scripts/validate-markdown.sh" \
  "$WORKDIR/<changed-path>" \
  --reference "/tmp/od-contrib-orig-<basename>"

# 새 file(예: 새 blog post)인 경우 --reference를 생략합니다.
# validator는 relative-ref check를 건너뜁니다.
```

**3c.7** `templates/PR-BODY-docs.md`를 `{{ONE_LINE_SUMMARY}}`, `{{DETAILS}}`, `{{FILES_LIST}}`, `{{DISCORD_INVITE}}`로 render합니다.

→ **Step 7**로 이동합니다.

---

### Step 3d — Bug report (issue path, PR 없음)

**3d.1** 현재 schema를 실제로 읽어 맞춥니다.

```bash
gh api "repos/${TARGET_REPO}/contents/.github/ISSUE_TEMPLATE/bug-report.yml" --jq .content | base64 -d > /tmp/od-bug-report.yml
```

schema가 template(`templates/ISSUE-BODY-bug.md`)와 달라졌다면 body를 맞게 다시 생성합니다.

**3d.2** critical field마다 `AskUserQuestion`을 하나씩 합니다. YAML field name이 아닌 plain language를 사용합니다.

| Bug-report field | 사용자에게 보일 prompt |
|---|---|
| `description` | "무엇이 잘못됐나요? 한 문장이어도 됩니다." |
| `steps` | "어떻게 재현하나요? 단계별로 알려 주세요." |
| `expected` | "어떤 결과를 기대했나요?" |
| `version` | "어떤 OD version인가요? (About menu 또는 `od --version`)" |
| `platform` | dropdown: macOS (Apple Silicon) / macOS (Intel) / Windows / Linux / Other |
| `logs` | "붙여 넣을 error log가 있나요? 없으면 건너뛰세요." |
| `screenshots` | "screenshot path가 있나요? 없으면 건너뛰세요." |

위 prompt는 모두 runtime에서 사용자의 chat 언어로 번역합니다.

**3d.3** 자동 수집할 수 있는 내용(사용자에게 묻지 않음)은 다음입니다.

- `uname`의 OS family
- relevant한 경우 `node -v`의 Node version

**3d.4** Dedupe합니다. description에서 keyword 3–5개를 뽑아 다음을 실행합니다.

```bash
gh search issues "<keywords>" --repo "$TARGET_REPO" --state open --limit 5 --json number,title,url
```

일치 항목이 있으면 `AskUserQuestion`으로 사용자의 chat 언어로 묻습니다. “기존 issue가 관련 있어 보입니다. (a) 기존 것에 comment, (b) 그래도 새 issue, (c) 취소 중 무엇을 할까요?”

**3d.5** 새 issue를 진행한다면 `templates/ISSUE-BODY-bug.md`를 render해 제출합니다.

```bash
bash "$SKILL_DIR/scripts/create-issue.sh" \
  --title "$TITLE" \
  --body-file "$WORKDIR_OR_TMP/.od-contrib/ISSUE-BODY.md" \
  --dedupe-keywords "<keywords>"
```

**3d.6** issue URL을 단독 line으로 출력합니다. 이 branch에서 branch를 push하거나 PR을 열지 않습니다.

---

## Step 7 — Preview + confirm (PR branch 공통)

사용자에게 다음처럼 깔끔한 summary를 보여 줍니다.

```text
About to commit:
  Branch:  od-contrib/<type>/<slug>-<date>
  Files:
    + skills/foo/SKILL.md            (1.2 KB)
    + skills/foo/preview.png         (54 KB)
  Push to:  <fork or upstream>
  Open PR:  nexu-io/open-design:main ← <fork>:<branch>
```

그다음 `git -C "$WORKDIR" diff --stat`과 rendered PR body의 `head -40`을 보여 visual sanity-check합니다.

필수 `AskUserQuestion` confirmation(사용자의 언어로 번역): **“이 PR을 push할까요?”**. 세 option은 다음입니다.

- **Ship it** — Step 8로 진행
- **Let me revise** — 해당 Step 3 sub-step으로 돌아감
- **Cancel** — workspace를 disk에 남기고 나중에 돌아올 수 있도록 path를 알린 뒤 종료

명시적인 “Ship it” 없이 절대 push하지 않습니다.

## Step 8 — Push & open PR

```bash
bash "$SKILL_DIR/scripts/create-pr.sh" \
  --workdir "$WORKDIR" \
  --type "<skill|design-system|i18n|docs>" \
  --title "<PR title from references/newcomer-tone.md>" \
  --body-file "$WORKDIR/.od-contrib/PR-BODY.md"
```

PR URL을 단독 line으로 출력합니다. 완료입니다.

---

## Safety rails (필수)

- `main` / `master` / `develop`에 절대 push하지 않습니다. push script가 거부합니다.
- `--force` push를 절대 하지 않습니다.
- 모든 workspace activity는 `$OD_WORK_ROOT`(기본 `$HOME/od-contrib-work`) 아래에만 둡니다. `od::assert_in_workroot`가 이를 강제합니다.
- bug-report path는 `gh issue create` 전에 항상 dedupe search를 합니다.
- 사용자 memory를 존중합니다. contributor lookup에서 GitHub user `xxiaoxiong`은 제외합니다(`[[feedback_no_outreach_xxiaoxiong]]`).

## 이 skill을 쓰지 말아야 할 때

- daemon/web bug를 수정하거나 code change로 feature를 추가하려는 경우 → `auto-github-contributor`를 사용하세요(TDD loop가 있습니다). 이 skill은 content path에는 lint/typecheck/test가 필요 없으므로 의도적으로 실행하지 않습니다.
- Skill / Design System을 처음부터 **생성**하려는 경우 → 그것은 OpenDesign 자체가 할 일입니다. 먼저 OD를 실행해 artifact를 얻은 뒤 여기로 돌아와 올리세요.

> 번역 범위: 고정 SHA의 `.claude/skills/od-contribute/SKILL.md:1-320`을 구조 보존해 번역했다. 명령·파일 경로·식별자·권한 이름은 원문대로 유지했다. [S20]
