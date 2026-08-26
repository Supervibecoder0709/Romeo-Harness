# 빠른 시작

## 새 프로젝트

```bash
# rulesync를 전역 설치
npm install -g rulesync

# 필요한 디렉터리, 예제 규칙 파일, 설정 파일 생성
rulesync init

# 공식 스킬 설치(권장)
rulesync fetch dyoshikawa/rulesync

# 또는 rulesync.jsonc에 스킬 소스를 추가한 뒤 'rulesync install' 실행(“선언형 스킬 소스” 참고)
```

## 기존 AI 도구 설정

이미 AI 도구 설정이 있다면:

```bash
# 기존 파일 가져오기(.rulesync/**/*로)
rulesync import --targets claudecode    # CLAUDE.md에서
rulesync import --targets cursor        # .cursorrules에서
rulesync import --targets copilot       # .github/copilot-instructions.md에서
rulesync import --targets claudecode --features rules,mcp,commands,subagents

# 더 많은 도구 지원

# 모든 feature를 포함한 통합 설정 생성
rulesync generate --targets "*" --features "*"
```

## 빠른 명령

모든 명령과 옵션의 종합 목록은 [CLI Commands](/reference/cli-commands)를 참고한다.

> 번역 원문: `docs/getting-started/quick-start.md` at `c3acceacec5463efe14ebb1b8be5fed5fa835e65`. [S11]
