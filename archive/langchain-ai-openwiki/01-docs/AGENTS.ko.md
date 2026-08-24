## OpenWiki

이 repository의 문서는 `/openwiki` directory에 있습니다.

여기서 시작하세요.

- [OpenWiki quickstart](openwiki/quickstart.md)

OpenWiki에는 repository overview, architecture note, workflow, domain concept, operation, integration, testing guidance, source map이 포함됩니다.

이 repository에서 작업할 때는 먼저 OpenWiki quickstart를 읽고, 그 link를 따라 관련 architecture, workflow, domain, operation, testing note를 읽습니다.

<!-- OPENWIKI:START -->

## OpenWiki

이 repository에는 생성된 `openwiki/` evidence index가 있습니다. 필수 startup reading이 아니라 필요할 때 읽는 optional context입니다.

- source code와 test를 authoritative로 취급합니다. brief의 unknown과 review item은 verification gap이지 자동 requirement가 아닙니다.
- 바뀐 behavior를 증명하는 가장 좁고 조용한 validation을 우선합니다. 완전한 failure output을 보존합니다.

scheduled OpenWiki GitHub Actions workflow는 repository wiki를 refresh합니다. 명시적으로 요청받지 않았다면 생성된 OpenWiki page를 직접 edit하지 말고, source code/doc을 갱신한 뒤 OpenWiki가 regenerate하게 합니다.

<!-- OPENWIKI:END -->
