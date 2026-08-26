원문: agent-skills/game-development/ship-web-games/SKILL.md  
고정 근거: [E10]

---
name: ship-web-games
description: 플레이 가능한 Three.js 또는 web game을 package, deploy, verify한다. release build, asset delivery, private/public deployment, production smoke test, browser proof, release note, rollback readiness, temporary QA resource cleanup에 사용한다.
---

# Web Game 출고

검증한 commit만 release하고 local build가 아니라 deployed game을 증명한다.

## Release 순서

1. 정확한 integration commit을 확인하고 관련 없는 작업을 보존한다.
2. focused test, lint/type check, production build, diff check를 실행한다.
3. 검증한 정확한 commit을 package하고 deploy한다.
4. deployment status를 poll하고 repository-approved browser에서 production game을 연다.

## Production proof

load, 첫 input, 한 combat 또는 core interaction, asset, 해당 시 save/settings, responsive view, console health, representative performance를 확인한다. deployed state는 local readiness와 별도로 보고한다.

## 깨끗하게 끝내기

release evidence와 rollback target을 기록한다. 임시 dev server, benchmark, QA tab은 더 이상 필요 없을 때 닫되, 다른 활성 task가 소유한 resource는 종료하지 않는다.
