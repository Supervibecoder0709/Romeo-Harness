# 개발

## 다른 local repository를 대상으로 실행

사전 요구 사항:

- Node.js 20 이상
- pnpm

이 machine에서 `pnpm link --global`이 아직 동작하지 않았다면 pnpm의 global bin directory를 한 번 설정합니다.

```sh
pnpm setup
```

shell을 재시작하거나 `pnpm setup`이 변경한 profile file을 source합니다. 그런 뒤 이 package를 setup하고 link합니다.

```sh
cd /path/to/openwiki
pnpm install
pnpm run build
pnpm link --global
```

OpenWiki가 검사할 repository에서 dry test를 실행합니다.

```sh
cd /path/to/target/repo
OPENWIKI_DEV=1 openwiki --dry-run
```

target repository에서 실제 CLI를 실행합니다.

```sh
cd /path/to/target/repo
openwiki
openwiki -p "Summarize what you can do"
openwiki --modelId openai/gpt-5.5
openwiki "Please focus on API documentation"
```

target repository는 여전히 current working directory입니다. global link는 `dist/cli.js`의 path를 입력하지 않아도 되게 할 뿐입니다.

pnpm global을 구성하고 싶지 않다면 shell alias를 대신 사용합니다.

```sh
alias openwiki='node /path/to/openwiki/dist/cli.js'
```

이를 지속하려면 `~/.zshrc`에 넣을 수 있습니다.

OpenWiki source code를 바꾼 뒤에는 이 package directory에서 rebuild합니다.

```sh
pnpm run build
```

기존 global link는 rebuild된 `dist/cli.js`를 계속 사용합니다.

실제 run은 다음을 쓸 수 있습니다.

- `openwiki/`
- local OpenRouter model/key 설정과 optional LangSmith credential을 위한 `~/.openwiki/.env`

Scheduled update workflow example:

- `examples/openwiki-update.yml`
