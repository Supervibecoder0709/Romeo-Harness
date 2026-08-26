# OpenWiki에 기여하기

기여해 주셔서 감사합니다! PR 기여의 표준은 **PR 하나 = 변경 하나**입니다. 이렇게 해야 review가 빠르고 repository history가 깔끔하게 유지됩니다.

## 범위: PR 하나 = 변경 하나

Pull request는 범위가 잘 정리되어야 하며 각각 정확히 한 가지를 해야 합니다.

현재 변경의 일부인 bug를 고치는 것은 괜찮습니다. 하지만 작업 중 _관련 없는_ 문제까지 고치고 있다면 별도 PR을 여세요.

### "좁은 범위"의 의미

✅ **좋음:** "Add Fireworks to the model provider list" — provider config, model option, doc line.

❌ **너무 넓음:** "Add a new provider, refactor the credential onboarding flow, and fix a typo in the README" — 관련 없는 세 가지 변경입니다. 세 PR로 나누어야 합니다.

## PR을 열기 전

CI에서 뜻밖의 일을 겪지 않도록 local에서 다음을 실행합니다.

```sh
pnpm run format
pnpm run lint
pnpm test
```

`format`, `lint`는 모든 PR에서 실행되는 check와 일치하며, `test`는 typecheck, build, coverage가 있는 Vitest suite를 실행합니다.

## Coding-agent integration을 local에서 test하기

현재 checkout 기반 integration은 다음으로 설치합니다.

```sh
pnpm integrations:dev <codex|claude>
```

이 command는 OpenWiki를 build하고 host skill을 refresh하며, 현재 Node executable과 `dist/cli/cli.js`의 absolute path를 기록합니다. 설치 뒤 coding agent를 재시작하세요. Codex와 Claude Code는 user scope에 설치됩니다. 나중의 source change에는 bundled skill 자체가 바뀌지 않는 한 `pnpm build`만 필요합니다. skill을 refresh하거나 Node installation을 바꾼 뒤에는 `integrations:dev`를 다시 실행합니다.

## Coding-agent integration 추가

OpenWiki host integration은 canonical skill 하나와 MCP tool 네 개를 공유합니다: `openwiki_begin`, `openwiki_inspect_claims`, `openwiki_resolve_claims`, `openwiki_finish`. skill을 복사하거나 host-specific tool을 추가하지 말고 registry와 config boundary에 host-specific behavior를 추가합니다.

1. host가 repository skill과 local stdio MCP server를 발견하는지 확인합니다. 지원하는 user/project path를 문서화하고, 지원하지 않는 user scope에는 global skill location을 만들어 내지 말고 `null`을 사용합니다.
2. `src/integrations/install/types.ts`의 `HostTargetId`에 host ID를 추가한 뒤, `src/integrations/install/registry.ts`의 `HOST_TARGETS`에 display name, provenance actor, 지원 path, MCP config kind, documentation URL을 추가합니다.
3. 가능하면 JSON 또는 Codex TOML config adapter를 재사용합니다. host가 진짜로 다른 config format을 쓸 때만 focused adapter를 추가하되, 관련 없는 user config와 정확한 ownership check를 보존합니다.
4. focused registry, install/status/uninstall, config-conflict, packaging, provenance test를 추가합니다. unsupported scope를 pin하고 project install이 Git root로 resolve되는지 확인합니다.
5. 실제 host smoke test에 `pnpm integrations:dev <host>`를 실행한 뒤 `pnpm test`, `pnpm run lint:check`, `pnpm run format:check`를 실행합니다.
6. README usage example을 갱신하고 user-visible support에는 changeset을 추가합니다.

v1 boundary를 좁게 유지합니다. host agent는 native repository tool로 조사와 Markdown authoring을 하고, OpenWiki는 deterministic preparation, finalization, metadata, provenance, managed setup file을 소유합니다.

변경을 release해야 한다면 changeset도 추가합니다(아래 참고).

## Changeset

[Changesets](https://github.com/changesets/changesets)로 release합니다. PR이 사용자가 알아야 할 방식으로 published `openwiki` package를 바꾼다면(bug fix, new feature, 모든 behavior change) changeset을 추가합니다.

```sh
pnpm changeset
```

bump type을 고르고 짧은 summary를 쓴 다음 생성된 `.changeset/*.md` file을 PR과 함께 commit합니다. summary는 changelog entry가 되므로 reviewer가 아니라 user를 위해 씁니다. bump type은 semver를 따릅니다.

- **patch**: bug fix와 그 밖의 작은 backward-compatible change
- **minor**: 새로운 backward-compatible feature
- **major**: breaking change

published package에 영향을 주지 않는 변경(doc, test, CI, internal refactor)에는 changeset이 필요 없습니다. package를 건드리지만 release를 만들지 않아야 한다면 빈 changeset `pnpm changeset --empty`로 의도를 기록합니다.

PR이 merge되면 Release workflow가 pending changeset을 모으는 "chore: version packages" PR을 엽니다. 그 PR을 merge하면 version이 bump되고 `CHANGELOG.md`가 갱신되며 release를 publish합니다.

## PR 기대 사항

- **명확한 title** — `feat:`, `fix:`, `chore:` 같은 [Conventional Commits](https://www.conventionalcommits.org/) type을 앞에 붙인, 한 가지 변경을 설명하는 한 문장(예: `feat: add Fireworks to the model provider list`).
- **무엇을, 왜** — PR이 하는 일과 이유를 짧게 설명.
- **어떻게 test했는가** — 변경이 동작하고 기존 behavior를 깨지 않는 unit/end-to-end test를 설명. test를 추가/수정했다면 여기에 적음.
- **Changeset 추가** — user-facing change는 changelog와 다음 release에 들어가도록 추가. [Changesets](#changesets) 참고.
- **Issue link** — trivial하지 않은 일은 context가 남도록 issue 연결.

## AI agent에게

이 repository에서 PR을 여는 agent라면 이 규칙은 구속력이 있습니다. 변경을 단일 concern에 좁게 유지하세요. 만들려는 변경이 이 문서의 어떤 내용이라도 위반한다면 진행하지 말고 human에게 알려야 합니다.

## Close되는 항목

관련 없는 변경을 여러 개 묶은 PR은 분리 요청과 함께 close될 수 있습니다.
