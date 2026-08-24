# Design Tokens Community Group

이 저장소(또는 “repo”)는 [Design Tokens Community Group](https://www.w3.org/community/design-tokens/)의 작업에 사용되며, [W3C Community License Agreement (CLA)](https://www.w3.org/community/about/agreements/cla)의 적용을 받습니다. 실질적인 기여를 하려면 [Community Group](https://www.w3.org/community/design-tokens/)에 가입해야 합니다.

자세한 내용은 커뮤니티 그룹 헌장의 [Contribution Mechanics 섹션](https://github.com/design-tokens/community-group/blob/main/CHARTER.md#contrib)을 읽으세요.

---

기여(pull request)에 본인 외의 기여자가 있다면, pull request 댓글에서 모든 기여자를 식별해 주세요.

기여자(본인 외; 본인은 자동으로 추가됨)를 추가하려면 한 줄에 한 명씩 다음과 같이 표시합니다.

```diff
+ @github_username
```

기여자를 잘못 추가했다면 댓글에서 다음과 같이 제거할 수 있습니다.

```diff
- @github_username
```

다른 사람을 대신해 pull request를 만들지만 기능 설계에는 참여하지 않았다면, 위 문법으로 자신을 제거할 수 있습니다.

## 커뮤니티 토론

실시간 커뮤니티 채팅을 위해 [공식 DTCG Discord 서버](https://discord.gg/fkK6ZUXRkp)에 참여하세요.

버그 보고, 명세 제안, 구체적인 repo 변경에는 [GitHub issues](https://github.com/design-tokens/community-group/issues)를 사용하세요.

## 로컬 개발

다음 섹션은 로컬 컴퓨터에서 designtokens.org와 기술 보고서를 미리보기 위한 것입니다.

### 설정

이 repo에는 [Node.js](https://nodejs.org/en)와 [pnpm](https://pnpm.io/)이 설치되어 있어야 합니다(Node.js 버전을 여러 개 관리해야 한다면 [fnm](https://github.com/Schniz/fnm)을 강력히 권장합니다). 둘 다 설치한 뒤, 이 [repository를 로컬로 clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)하고 프로젝트 루트의 터미널에서 다음을 실행하세요.

```sh
pnpm i
pnpm run install-browsers
pnpm run dev
```

로컬 사이트는 [localhost:4321](http://localhost:4321)에서 사용할 수 있습니다.

### 명령

다음 명령은 **프로젝트 루트**에서 실행할 수 있습니다.

| 명령                    | 설명                                         |
| :---------------------- | :------------------------------------------- |
| `pnpm run dev`          | 개발 모드로 designtokens.org를 실행합니다.   |
| `pnpm run lint`         | 프로젝트를 lint합니다.                       |
| `pnpm run spellcheck`   | [맞춤법 검사](#spellcheck)를 실행합니다.     |
| `pnpm run build`        | 웹사이트의 정적 build를 만듭니다.            |

> [!NOTE]
> `www`와 `technical-reports` 폴더에도 `pnpm run dev` 명령이 있습니다. 이 명령은 워크플로의 일부만 실행하므로 디버깅 용도로만 사용해야 합니다.

### 프로젝트 구조

이 repo에는 서로 다른 프로젝트를 담은 다음 하위 디렉터리가 있습니다.

| 디렉터리               | 설명                           |
| :--------------------- | :----------------------------- |
| `meeting-notes/`       | 지난 회의의 기록입니다.         |
| `technical-reports/`   | 디자인 토큰 명세입니다.         |
| `www/`                 | designtokens.org 코드입니다.    |

### 맞춤법 검사

이 프로젝트는 맞춤법 검사에 [cSpell](https://cspell.org/)을 사용합니다. 맞춤법 검사는 대소문자를 구분하므로 Bézier 또는 GitHub 같은 단어의 올바른 대문자 사용을 감지합니다.

[cspell/](./cspell/) 폴더에 추가하여 단어를 전역 허용하거나 전역 차단할 수 있습니다. 자세한 내용은 [cSpell 사전 문서](https://cspell.org/docs/dictionaries/)를 참조하세요.

목록에 추가하지 않고 개별 항목을 무시하려면 `// cSpell: disable` 주석이나 `// cSpell:words [쉼표로 구분한 단어 목록]` 주석을 추가하세요. 자세한 내용은 [cSpell 문서의 overrides]https://cspell.org/docs/Configuration/document-settings#words)를 참조하세요.

## 보고서 발행

> [!NOTE]
> 이는 명세 편집자만 수행해야 합니다.

다음은 보고서의 새 릴리스를 만드는 일반 단계입니다.

### 설정

다음 단계는 로컬 사본을 정리하고 업데이트하여 이상적인 상태로 만듭니다. 이는 손상된 캐시와 새 버전에 포함되어서는 안 되는 우발적인 로컬 파일 같은 발행 오류를 방지합니다.

1. **최신 내용 가져오기**: `git pull`
1. **로컬 repo 초기화**(선택이지만 권장): `git clean -dfx` (⚠️ 추적되지 않는 파일을 모두 지웁니다. 보관할 임시 파일이 있다면 먼저 repo 밖으로 옮기세요.)
1. **의존성 재설치**: `pnpm i`

### 버전 관리

1. **ReSpec 업데이트**: 다른 모든 보고서와 함께 [technical-reports/TR/index.html](technical-reports/TR/index.html)의 정보를 업데이트합니다. 다음을 포함하되 이에 한정하지 않습니다.
   - build를 위해 [isPreview](https://respec.org/docs/#isPreview)는 반드시 `false`여야 합니다. ⚠️ 이 변경은 commit하지 마세요.
   - [subtitle](https://respec.org/docs/#subtitle)
   - [specStatus](https://respec.org/docs/#specStatus)
   - [prevVersion](https://respec.org/docs/#latestVersion)
   - 자세한 내용은 [ReSpec 문서](https://respec.org/docs/)를 참조하세요.
2. **build 실행**: `pnpm run build`
3. **이름 변경**: `www/src/pages/TR/drafts`를 `www/src/pages/TR/[new version]`으로 이름 변경합니다. 이 폴더를 반드시 commit하세요!
4. **표 업데이트**: [www/src/pages/technical-reports.md](www/src/pages/technical-reports.md)를 업데이트합니다.

끝나면 `www/src/pages/TR/[new version]`에서 commit할 수 있는 변경사항이 보여야 합니다. 이것은 이제 영구 버전이 되며, 모든 변경은 수동으로 추적됩니다.
