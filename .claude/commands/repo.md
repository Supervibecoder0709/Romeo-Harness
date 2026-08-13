---
description: GitHub 레포를 별도 Codex 워크트리에서 분석해 한국어 아카이브를 만든다.
argument-hint: <github-url> [--replace] [--staged]
---

# /repo

`$ARGUMENTS`에서 URL 앞의 `@`를 하나 제거한 뒤 GitHub URL 하나, 선택적 `--replace`, 선택적 `--staged`를 파싱한다. 따라서 아래 두 입력은 같다.

```text
/repo https://github.com/<owner>/<repo>
/repo @https://github.com/<owner>/<repo>
```

URL이 없거나 `https://github.com/<owner>/<repo>` 형식이 아니면 실행하지 말고 사용법을 안내한다. URL 안의 branch/path는 source ref 선택에만 사용하며, archive 이름은 `<owner>-<repo>`로 고정한다.

## 역할

이 명령은 **Claude가 코디네이터이고 Codex가 분석 작업자**인 얇은 어댑터다. 이 명령 자체가 레포 내용을 추측하거나 분석하지 않는다. Codex 작업자에게 `$repo-archive`를 실행하게 한 뒤 산출물만 현재 워크트리로 가져온다.

## 실행

1. `orca status --json`으로 runtime이 준비됐는지, `gh auth status`로 GitHub 읽기 인증이 되는지 확인한다. 실패하면 정확한 오류와 필요한 복구만 보고하고 중단한다.
2. 현재 워크트리의 `archive/<owner>-<repo>/` 존재 여부를 먼저 확인한다.
3. 대상이 있고 `--replace`가 없으면, 기존 경로를 보여주고 중단한다. 대상이 있고 `--replace`가 있으면, 교체 대상·영향·복구 방법을 설명하고 **현재 대화에서 다시 승인을 받는다**. 이 재확인 전에는 worker를 시작하거나 파일을 지우지 않는다.
4. `orca worktree current --json`에서 현재 Harness worktree의 `repoId`를 얻는다. 새 자식 worktree를 만드는 `worker-start`에는 `path:$PWD`가 아니라 이 정확한 `id:<repoId>`를 사용한다.
5. `orca orchestration run-create --objective "Archive <owner>/<repo> in Korean" --json`으로 Run을 만든다.
6. `skills/repo-archive/SKILL.md`의 절대 경로를 현재 coordinator worktree에서 계산한다. 새 child worktree는 커밋되지 않은 `.agents/skills` 변경을 포함하지 않을 수 있으므로, `orca orchestration task-create`의 작업 설명에는 `$repo-archive` 사용과 함께 이 `source skill path`를 넣는다. Worker는 `$repo-archive`가 discovery 목록에 없으면 해당 절대 경로의 `SKILL.md`를 읽어 같은 절차를 수행한다. 절대 경로도 읽을 수 없으면 `BLOCKED_SKILL_UNAVAILABLE`로 실패 보고한다.

   Shell에서 작업 설명을 만들 때 `$repo-archive`의 `$`가 변수로 확장되지 않도록 단일 인용부호 또는 `\$repo-archive`를 사용한다. 작업 설명에는 GitHub 읽기 전용, worker worktree의 `archive/<owner>-<repo>/` 작성, 고정 SHA·생성 경로·근거 공백·완료 상태를 `worker_done`으로 보고한다는 조건도 포함한다.
7. 아래 기본 실행을 사용한다. `--model`과 `--effort`를 생략해 현재 Orca 계정의 기본 Codex 모델을 사용한다. Orca가 사람이 읽는 `sol` 별칭이 아니라 계정별 opaque provider ID를 요구하므로, 검증하지 않은 모델 이름을 넣어 실행을 막지 않는다.

```bash
orca orchestration worker-start \
  --run <run-id> \
  --task <task-id> \
  --worktree new-child \
  --agent codex \
  --name repo-<owner>-<repo> \
  --repo id:<current-worktree-repoId> \
  --setup inherit \
  --timeout-ms 3600000 \
  --json
```

8. `orca orchestration check --wait --types worker_done,escalation,question --timeout-ms 900000 --json`로 대기한다. 질문·실패·시간 초과를 성공으로 간주하지 않는다.
9. 성공한 worker의 `archive/<owner>-<repo>/`만 현재 워크트리의 같은 위치로 복사한다. 이미 승인한 `--replace`인 경우에만 기존 대상 전체를 교체한다.
10. `bash scripts/validate-repo-archive.sh archive/<owner>-<repo>`를 실행한다. 실패하면 생성물은 `미검증`으로 보고하고 성공으로 말하지 않는다.
11. 검증 결과와 worker 출력이 보존된 뒤 `orca orchestration worker-release --dispatch <dispatch-id> --json`으로 정확히 그 완료 worker 터미널만 해제한다. 통과했을 때만 경로·SHA·문서 수·미확인을 보고한다.

## 대형 레포의 선택적 모델 분리

`--staged`가 명시되고 각 단계의 **검증된 provider model ID**가 제공된 경우에만 이 경로를 사용한다. 기본값을 세 모델 파이프라인으로 바꾸지 않는다. 후보가 40개 이상이거나 다중 패키지 레포일 때 다음처럼 순차 실행한다.

1. `luna`: `_staging/discovery.md`만 작성한다. 읽기·경로 분류·근거 위치 수집만 한다.
2. `sol`: discovery artifact와 원문 근거를 다시 열어 중요도 판별 및 `00`, `02`, `04`, `05` 문서를 작성한다.
3. `terra` 또는 `luna`: 확정된 번역 파일만 작성한다.

세 작업은 같은 워크트리에서 순차로 실행하거나, 이전 산출물을 다음 작업자에게 명시적으로 전달해야 한다. 별도 병렬 워크트리에 같은 `archive/`를 쓰게 하면 결과가 자동 합쳐지지 않는다. 실제 provider ID가 확인된 경우에만 각 `worker-start` 호출에서 `--model`과 `--effort`를 다르게 준다. 하나라도 확인되지 않았으면 기본 Codex 작업자 한 명으로 실행한다.
