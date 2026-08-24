# 드라이 런

Rulesync는 `generate` 명령에 실제 파일을 쓰지 않고 어떤 변경이 이뤄질지 볼 수 있는 두 가지 드라이 런 옵션을 제공한다.

## `--dry-run`

파일을 실제로 쓰지 않고 무엇이 쓰이거나 삭제될지를 보여 준다. 변경 사항에는 `[DRY RUN]` 접두사가 표시된다.

```bash
rulesync generate --dry-run --targets claudecode --features rules
```

## `--check`

`--dry-run`과 같지만 파일이 최신 상태가 아니면 종료 코드 1로 끝난다. 생성된 파일이 커밋됐는지 CI/CD 파이프라인에서 검증할 때 유용하다.

```bash
# CI 파이프라인에서
rulesync generate --check --targets "*" --features "*"
echo $?  # 최신이면 0, 변경이 필요하면 1
```

> [!NOTE]
> `--dry-run`과 `--check`는 함께 사용할 수 없다.

> 번역 원문: `docs/guide/dry-run.md` at `c3acceacec5463efe14ebb1b8be5fed5fa835e65`. [S12]
