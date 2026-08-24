# @dtcg/schemas

DTCG Format 및 Resolver 명세를 위한 원본 JSON Schema입니다. 유지보수성을 위해 여러 파일로 나뉘어 있고, 호스팅을 위해 하나의 자체 포함 파일로 번들됩니다.

## 구조

```
src/              원본 schema(분할 파일, `$ref` 포함)
dist/             번들 출력(생성물, gitignore됨)
scripts/          build 도구
schemas.config.json  번들 설정
```

## 사용법

```sh
pnpm --filter @dtcg/schemas run build
```

이 명령은 모든 원본 schema를 등록하고, 각 entry schema를 하나의 파일로 번들한 뒤 출력을 `dist/`와 `../www/public/schemas/` 모두에 기록합니다.

## 설정

버전 또는 entry schema를 추가하려면 `schemas.config.json`을 편집하세요.

```json
{
  "versions": [
    {
      "version": "2025.10",
      "entrySchemas": [
        {
          "id": "https://www.designtokens.org/schemas/2025.10/format.json",
          "filename": "format.json"
        }
      ]
    }
  ],
  "sourceDir": "src",
  "distDir": "dist",
  "outputDirs": ["dist", "../www/public/schemas"]
}
```

- **`versions[].version`**: 명세 버전(예: `"2025.10"`)입니다. `sourceDir`와 각 output dir 아래의 하위 디렉터리를 결정합니다.
- **`versions[].entrySchemas`**: 이 명세 버전에 번들할 root schema입니다. 각 entry는 모든 `$ref`가 해결된 자체 포함 출력 파일 하나를 만듭니다. `id`는 schema의 `$id` URI이고, `filename`은 출력 파일명입니다.
- **`sourceDir`**: 이 패키지를 기준으로 한, 분할된 원본 schema가 있는 디렉터리입니다.
- **`distDir`**: 이 패키지를 기준으로 한 번들 출력 디렉터리입니다.
- **`outputDirs`**: 이 패키지를 기준으로 한, 출력할 모든 경로입니다. 각각 `<version>/` 하위 디렉터리를 갖습니다.

## 새 schema 버전 추가

[CONTRIBUTING.md](CONTRIBUTING.md)를 참조하세요.
