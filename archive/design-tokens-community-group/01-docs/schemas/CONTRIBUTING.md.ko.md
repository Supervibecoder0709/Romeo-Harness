# 새 Schema 버전 기여하기

이 가이드는 기존 버전과 나란히 DTCG schema의 새 버전을 추가하는 방법을 설명합니다(예: `2025.10` 옆에 `2026.04` 추가).

## 사전 조건

먼저 현재 schema를 build할 수 있는지 확인하세요.

```sh
pnpm --filter @dtcg/schemas run build
```

## 단계

### 1. 원본 디렉터리 만들기

기존 버전을 시작점으로 복사한 뒤 변경하세요.

```sh
cp -r src/2025.10 src/<new-version>
```

### 2. `$id` URI 업데이트

`src/<new-version>/` 아래의 모든 schema 파일에는 버전이 포함된 `$id`가 있습니다. 모두 새 버전을 반영하도록 업데이트하세요. 예를 들면:

```
https://www.designtokens.org/schemas/2025.10/format.json
```

은 다음으로 바뀝니다.

```
https://www.designtokens.org/schemas/<new-version>/format.json
```

이는 entry schema(`format.json`, `resolver.json`) 및 이들이 참조하는 모든 하위 schema(`format/token.json`, `format/values/color.json`, `resolver/set.json` 등)에 적용됩니다.

### 3. 명세 변경 적용

schema를 기술 보고서의 새 버전에 맞추어 업데이트하세요. 이는 그 버전의 명세 변경을 반영하기 위해 타입 정의, 속성, 제약 조건을 추가·제거·수정하는 것을 뜻합니다.

### 4. `const` 값 업데이트

일부 schema는 버전을 `const`로 고정합니다. 예를 들어 `resolver.json`에는 다음이 있습니다.

```json
"version": {
  "const": "2025.10"
}
```

이를 새 버전 문자열과 일치하도록 업데이트하세요.

### 5. `schemas.config.json`에 버전 등록

`versions` 배열에 새 항목을 추가하세요.

```json
{
  "version": "<new-version>",
  "entrySchemas": [
    {
      "id": "https://www.designtokens.org/schemas/<new-version>/format.json",
      "filename": "format.json"
    },
    {
      "id": "https://www.designtokens.org/schemas/<new-version>/resolver.json",
      "filename": "resolver.json"
    }
  ]
}
```

build script는 이 설정을 읽어 번들할 버전을 파악합니다.

### 6. Build

```sh
pnpm --filter @dtcg/schemas run build
```

build는 각 entry schema를 `dist/<new-version>/` 아래의 자체 포함 파일 하나로 번들하고, 이를 `www/public/schemas/<new-version>/`으로 복사합니다.

## 구조 참고

```
src/
  <version>/
    format.json            Format 명세의 entry schema
    format/
      group.json
      groupOrToken.json
      token.json
      tokenType.json
      values/
        border.json
        color.json
        ...
    resolver.json          Resolver 명세의 entry schema
    resolver/
      modifier.json
      resolutionOrder.json
      set.json
dist/                      생성된 번들 출력(gitignore됨)
schemas.config.json        번들 설정
```
