# slugify

> 문자열을 slug로 변환

URL, 파일명, ID에 유용합니다.

[독일어(움라우트)](https://en.wikipedia.org/wiki/Germanic_umlaut), 베트남어, 아랍어, 러시아어를 포함한 대부분의 주요 언어를 처리합니다. [더 많은 언어](https://github.com/sindresorhus/transliterate#supported-languages)를 확인하세요.

## 설치

```sh
npm install @sindresorhus/slugify
```

## 사용법

```js
import slugify from '@sindresorhus/slugify';

slugify('I ♥ Dogs');
//=> 'i-love-dogs'

slugify('  Déjà Vu!  ');
//=> 'deja-vu'

slugify('fooBar 123 $#%');
//=> 'foo-bar-123'

slugify('я люблю единорогов');
//=> 'ya-lyublyu-edinorogov'
```

## API

### slugify(string, options?)

#### string

유형: `string`

slug로 변환할 문자열입니다.

#### options

유형: `object`

##### separator

유형: `string`\
기본값: `'-'`

```js
import slugify from '@sindresorhus/slugify';

slugify('BAR and baz');
//=> 'bar-and-baz'

slugify('BAR and baz', {separator: '_'});
//=> 'bar_and_baz'

slugify('BAR and baz', {separator: ''});
//=> 'barandbaz'
```

##### lowercase

유형: `boolean`\
기본값: `true`

slug를 소문자로 만듭니다.

```js
import slugify from '@sindresorhus/slugify';

slugify('Déjà Vu!');
//=> 'deja-vu'

slugify('Déjà Vu!', {lowercase: false});
//=> 'Deja-Vu'
```

##### decamelize

유형: `boolean`\
기본값: `true`

camelCase를 분리된 단어로 변환합니다. 내부적으로 `fooBar` → `foo bar`로 처리합니다.

```js
import slugify from '@sindresorhus/slugify';

slugify('fooBar');
//=> 'foo-bar'

slugify('fooBar', {decamelize: false});
//=> 'foobar'
```

##### customReplacements

유형: `Array<string[]>`\
기본값: `[
	['&', ' and '],
	['🦄', ' unicorn '],
	['♥', ' love ']
]`

사용자 정의 치환을 추가합니다.

치환은 다른 모든 변환보다 먼저 원본 문자열에서 실행됩니다.

`&`처럼 같은 키를 가진 항목을 설정할 때만 기본 치환을 덮어씁니다.

```js
import slugify from '@sindresorhus/slugify';

slugify('Foo@unicorn', {
	customReplacements: [
		['@', 'at']
	]
});
//=> 'fooatunicorn'
```

대시로 분리하려면 치환값의 앞뒤에 공백을 추가하세요.

```js
import slugify from '@sindresorhus/slugify';

slugify('foo@unicorn', {
	customReplacements: [
		['@', ' at ']
	]
});
//=> 'foo-at-unicorn'
```

또 다른 예시:

```js
import slugify from '@sindresorhus/slugify';

slugify('I love 🐶', {
	customReplacements: [
		['🐶', 'dogs']
	]
});
//=> 'i-love-dogs'
```

##### preserveLeadingUnderscore

유형: `boolean`\
기본값: `false`

문자열이 밑줄로 시작하면 slug화된 문자열에도 그 밑줄을 보존합니다.

선행 밑줄이 의도적인 경우가 있습니다. 예를 들어 웹사이트에서 숨김 경로를 나타내는 파일명입니다.

```js
import slugify from '@sindresorhus/slugify';

slugify('_foo_bar');
//=> 'foo-bar'

slugify('_foo_bar', {preserveLeadingUnderscore: true});
//=> '_foo-bar'
```

##### preserveTrailingDash

유형: `boolean`\
기본값: `false`

문자열이 대시로 끝나면 slug화된 문자열에도 그 대시를 보존합니다.

예를 들어 입력 필드에서 slugify를 쓰면, 사용자가 slug를 작성하는 것을 막지 않으면서도 유효성 검사를 할 수 있습니다.

```js
import slugify from '@sindresorhus/slugify';

slugify('foo-bar-');
//=> 'foo-bar'

slugify('foo-bar-', {preserveTrailingDash: true});
//=> 'foo-bar-'
```

##### preserveCharacters

유형: `string[]`\
기본값: `[]`

특정 문자를 보존합니다.

이 배열에는 `separator`를 넣을 수 없습니다.

예를 들어 URL을 slug화하면서 HTML fragment 문자 `#`는 보존하고 싶을 수 있습니다.

```js
import slugify from '@sindresorhus/slugify';

slugify('foo_bar#baz', {preserveCharacters: ['#']});
//=> 'foo-bar#baz'
```

##### locale

유형: `string`\
기본값: `undefined`

언어별 전사에 사용할 locale입니다.

더 자세한 정보는 [`@sindresorhus/transliterate` 패키지](https://github.com/sindresorhus/transliterate#locale)를 참고하세요.

```js
import slugify from '@sindresorhus/slugify';

slugify('Räksmörgås');
//=> 'raeksmoergas'

slugify('Räksmörgås', {locale: 'sv'});
//=> 'raksmorgas'
```

##### transliterate

유형: `boolean`\
기본값: `true`

Unicode 문자를 ASCII로 전사할지 여부입니다.

`false`이면 비 ASCII 문자는 전사되지 않고 보존됩니다. 전사가 필요하지 않을 때 성능을 개선할 수 있습니다.

```js
import slugify from '@sindresorhus/slugify';

slugify('Déjà Vu');
//=> 'deja-vu'

slugify('Déjà Vu', {transliterate: false});
//=> 'déjà-vu'
```

### slugifyWithCounter()

같은 문자열이 여러 번 나오는 상황을 처리하기 위해, 카운터가 포함된 `slugify(string, options?)`의 새 인스턴스를 반환합니다.

#### 예시

```js
import {slugifyWithCounter} from '@sindresorhus/slugify';

const slugify = slugifyWithCounter();

slugify('foo bar');
//=> 'foo-bar'

slugify('foo bar');
//=> 'foo-bar-2'

slugify.reset();

slugify('foo bar');
//=> 'foo-bar'
```

#### 카운터 사용 사례 예시

예를 들어 각 하위 섹션에 예시가 있는 여러 섹션의 문서가 있습니다.

```md
## Section 1

### Example

## Section 2

### Example
```

그런 다음 `slugifyWithCounter()`를 사용해 고유한 HTML `id`를 생성하면 anchor가 올바른 제목에 연결되도록 할 수 있습니다.

### slugify.reset()

카운터를 초기화합니다.

#### 예시

```js
import {slugifyWithCounter} from '@sindresorhus/slugify';

const slugify = slugifyWithCounter();

slugify('foo bar');
//=> 'foo-bar'

slugify('foo bar');
//=> 'foo-bar-2'

slugify.reset();

slugify('foo bar');
//=> 'foo-bar'
```

## 관련 항목

- [slugify-cli](https://github.com/sindresorhus/slugify-cli) - 이 모듈용 CLI
- [transliterate](https://github.com/sindresorhus/transliterate) - Unicode 문자를 전사로 라틴 문자로 변환
- [filenamify](https://github.com/sindresorhus/filenamify) - 유효하고 안전한 파일명으로 변환

---

원문: [`readme.md` 고정 SHA](https://github.com/sindresorhus/slugify/blob/7c318bd1aa4b4affab29761f15a9604323fe2a3b/readme.md). 코드·명령·식별자·링크 URL은 원문대로 유지한 한국어 번역이며, 분석은 [상위 아카이브 문서](../00-exploration.md)에 분리했다.
