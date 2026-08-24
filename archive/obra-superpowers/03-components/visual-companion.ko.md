# Visual companion 구성요소

> 원문 근거: [E14](../06-source-evidence.md#e14), [E23](../06-source-evidence.md#e23), [E25](../06-source-evidence.md#e25)~[E29](../06-source-evidence.md#e29).

## 역할

`brainstorming`의 선택적 visual companion은 mockup, diagram, layout comparison처럼 "읽는 것보다 보는 것이 더 명확한" 질문을 브라우저에서 보여 주기 위한 local server다. 일반 요구사항 질문에는 쓰지 않으며, agent는 처음으로 시각 질문이 필요한 때 별도 메시지로 사용 허가를 물어야 한다. [E14](../06-source-evidence.md#e14)

## 입력 → 처리 → 출력

```text
사용자 허가
  → start-server.sh [--open]
  → session/content의 HTML 변경 감시
  → 인증된 browser에 최신 screen 제공
  → WebSocket choice event를 state/events에 append
  → agent가 그 event를 다음 대화 판단에 사용
```

- `start-server.sh`는 기본 `127.0.0.1`, random high port, 4시간 idle timeout을 사용하고, project directory를 주면 `<project>/.superpowers/brainstorm/` 아래 session dir와 persistent port/token path를 쓴다. `--open`은 `BRAINSTORM_OPEN=1`을 설정한다. [E27](../06-source-evidence.md#e27)
- `server.cjs`는 `content/`와 `state/`를 만들고 HTML 변화를 watch해 browser reload event를 broadcast한다. choice가 있는 WS event는 `state/events`에 JSON Lines로 append한다. [E26](../06-source-evidence.md#e26) [E27](../06-source-evidence.md#e27)
- server는 `?key=` 또는 session cookie의 token을 constant-time 비교하고, security headers를 설정하며, WS는 same-origin Origin까지 검사한다. content file serving은 dotfile, directory, symlink/hard-link escape를 거부하도록 작성됐다. [E26](../06-source-evidence.md#e26)

## 수명·보안 경계

- session secret가 URL·server log·server info·token file에 들어갈 수 있음을 start script가 직접 설명하고 `umask 077`을 설정한다. token file write는 mode `0600`을 요청한다. [E25](../06-source-evidence.md#e25) [E27](../06-source-evidence.md#e27)
- idle timeout 또는 owner PID 종료 시 server는 WebSocket을 닫고 `state/server-stopped`를 쓴다. [E27](../06-source-evidence.md#e27)
- stop script는 PID file만 믿지 않고 PID command line의 per-start server instance ID까지 확인한다. 증명이 안 되면 stale PID로 처리하고 signal하지 않는다. `/tmp` session만 삭제한다. [E28](../06-source-evidence.md#e28)
- 테스트 source에는 authentication, same-origin WS, file isolation, idle shutdown, persisted-token permission과 reconnect 의도가 있다. 이 아카이브에서 test는 실행하지 않았으므로 현재 pass 여부는 미확인이다. [E23](../06-source-evidence.md#e23) [E29](../06-source-evidence.md#e29)

## 운영 추천

기본 loopback bind와 명시적 opt-in을 유지하세요. 원격/container 환경에서 `--host 0.0.0.0`를 쓰려면 source의 token gate만으로 배포 환경의 network exposure가 해결된다고 가정하지 말고, ingress·방화벽·session directory 권한·log retention을 별도 확인해야 합니다. 이 문단은 source 사실에 기반한 **운영 추천**입니다.
