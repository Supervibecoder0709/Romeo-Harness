# 05. PM Harness 운영 메모

## 추천 결론

이 저장소를 Harness로 운영한다면, **“콘텐츠 변경 → 로컬/CI 품질 증거 → 별도 WAI 배포 dispatch → 최종 사이트 readback”을 분리한 승인 게이트**를 하나의 기본 흐름으로 삼는 것이 가장 적합하다. 이유는 이 레포 자체가 서비스 데이터베이스나 독립 배포기를 갖는 구조가 아니라 정적 콘텐츠·예제·검증 파이프라인이고, 실제 공개 전환은 별도 레포 workflow dispatch라는 외부 쓰기 경계를 지나기 때문이다. [S5], [S15], [S20]-[S22]

## 확인된 입력 계약과 실행 단위

- **콘텐츠 단위:** 패턴 설명, 예제 HTML/CSS/JS, 그리고 해당 예제를 검사하는 `test/tests/*.js`가 함께 변할 수 있다. 대표 예제는 설명 table의 `data-test-id`와 test가 연결된다. [S8]-[S11]
- **검증 단위:** `npm test`는 lint와 AVA 회귀를 묶고, CI는 diff에 따라 관련 회귀만 고른다. 예제 또는 생성기 변경이면 reference table과 coverage 산출물도 최신이어야 한다. [S5], [S12]-[S15]
- **운영 단위:** main 배포, PR 미리보기, 정리는 이 레포가 직접 게시하는 것이 아니라 별도 WAI 레포로 workflow dispatch를 보내는 단계다. [S20]-[S22]
- **모델/에이전트:** agent/skill 정의가 없으므로 역할을 “AI가 알아서 판단한다”로 설계할 근거는 없다. 사람 작성자, npm 도구, GitHub Actions, 외부 WAI workflow가 확인된 역할이다. [S2], [S5]

## 승인 지점

1. **PR 병합 전:** 생성된 파일 diff, lint/회귀/link check 결과, coverage 공백을 사람이 확인한다. 특히 coverage workflow의 코멘트는 `|| true`로 생성되므로, 코멘트 존재만으로 통과라고 판정하면 안 된다. [S15], [S19]
2. **main 공개 전환:** main push는 WAI 배포 dispatch를 요청한다. 외부 workflow와 공개 사이트를 직접 바꾸는 경계이므로, 변경 범위·배포 대상·롤백할 이전 커밋을 승인 기록에 남긴다. 이 레포 파일에는 별도의 승인 UI나 롤백 구현이 확인되지 않았다. [S20]
3. **PR 미리보기/정리:** `pull_request_target` 기반 workflow는 head SHA·fork 정보를 외부 workflow로 전달하며, 종료/branch delete는 외부 branch 제거를 요청한다. PR 출처와 대상 branch를 사람이 확인하는 것이 바람직하다. [S21], [S22]

## 증거와 완료 판정

완료 판정은 최소한 아래 네 증거가 연결될 때 가능하다.

1. 콘텐츠·예제·테스트·생성 산출물의 고정 commit diff
2. 해당 commit/PR의 필요한 GitHub Actions job 성공과 coverage 보고
3. 외부 `wai-aria-practices` workflow dispatch 및 완료 기록
4. 최종 공개 URL에서 기대 콘텐츠가 보이는 readback

현재 소스 분석으로 확인된 것은 1번의 **구조와 설정**뿐이다. 특정 SHA에서 2~4번이 실제 성공했는지는 이 아카이브 범위에서 미검증이다. [S13], [S15], [S17], [S19]-[S22]

## 재실행·복구

- **재실행 가능:** lint, 회귀, reference table, coverage, link check 명령은 `package.json`에 선언되어 있다. 단, link check는 외부 네트워크 결과에 좌우되고, 생성기는 파일을 다시 쓴다. [S5], [S14], [S16]
- **변경 범위 주의:** regression selector는 관련 파일이 없으면 실행하지 않고, landmark 예제는 CI trigger/선택에서 제외된다. 재실행 전에 그 변경이 실제 테스트 대상인지 확인해야 한다. [S12], [S13]
- **복구:** 이 레포에 자동 롤백 코드나 배포 상태 저장소는 확인되지 않았다. 안전한 운영 가정은 “이전 검증 완료 commit을 별도 WAI 배포 입력으로 재지정할 수 있는지”를 외부 레포 운영자에게 먼저 확인하는 것이다. 이는 **추천**이며 구현 사실이 아니다.

## 권한·보안 경계

- 로컬 pre-commit은 포맷/생성 파일을 수정하고 stage할 수 있다. 자동화에 맡기더라도 변경된 파일 목록과 diff를 readback해야 한다. [S5], [S6]
- coverage workflow는 `pull_request_target`과 `issues: write`를 사용하며 PR head를 checkout한 뒤 코멘트를 갱신하도록 설정한다. 이 사실만으로 취약하다고 단정할 수는 없지만, PR 출처·권한·실행 로그를 배포 전 검토 대상으로 삼아야 한다. [S19]
- WAI 연동은 `W3CGRUNTBOT_TOKEN`을 사용한다. 토큰 값과 scope는 이 레포에서 읽지 않았으므로, 최소 권한 여부는 미확인이다. [S20]-[S22]

## 확장 판단

**추천:** 자동화의 성공 상태를 “workflow dispatch를 보냄”이 아니라 “외부 workflow 완료 + 공개 사이트 readback”까지로 모델링한다. 이 경계는 배포 실패를 단순히 내부 CI 성공으로 오판하는 문제를 막고, 배포 레포가 분리된 현재 구조와도 맞는다.

**추천이 달라지는 조건:** 별도 WAI 레포를 통합하거나, 이 레포에 직접 정적 호스팅·배포 상태 API·확정된 rollback workflow가 생기면, 공개 전환 게이트를 그 새 시스템에 맞춰 재설계해야 한다. 현재 고정 SHA에는 그런 직접 배포 구현을 확인하지 못했다. [S2], [S20]-[S22]
