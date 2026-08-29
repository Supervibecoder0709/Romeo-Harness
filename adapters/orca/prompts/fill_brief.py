#!/usr/bin/env python3
"""검토자 절차 파일(reviewer-brief.md)의 자리표시자를 채운다 — RUNBOOK §3.4·§3.7·§6.6 이 쓴다.

손으로 채우지 않는 이유(체크리스트 42): 「명령을 실행하지 않는다」 를 조건 없이 옮겨 적으면 읽기·검색이 셸 명령인 런타임의
검토자는 파일을 하나도 읽지 못한다. 런타임별 읽기 수단 한 줄은 이 어댑터가 붙이고, 코어 문구는 건드리지 않는다(C-C6).

    python3 adapters/orca/prompts/fill_brief.py --unit <id> --run <run-id> --evidence-run <run> \
        --base-sha <sha> --task-sha256 <sha256> --runtime codex|claude --mode base|rerun --out <파일>

검증: 남은 자리표시자 0 · HTML 주석 0 · 읽기 수단 문장 정확히 1개 · base 모드면 evidence-run == run-id.
출력 파일은 검토 대상 워크트리의 제외 경로(`.harness/runs/<id>/<run-id>/reviewer-brief.md`)에 두는 것을 권장한다.
"""
import argparse
import re
import sys
from pathlib import Path

TEMPLATE = Path(__file__).with_name("reviewer-brief.md")
PLACEHOLDER_RE = re.compile(r"<[a-z][a-z0-9-]*>")
MARKER = "\n---\n"

# 런타임별 읽기 수단 — 역할 계약의 read·search 가 그 런타임에서 무엇인가. 코어에는 이 문장이 없다(C-C6).
READ_MEANS = {
    "codex": ("읽기·검색은 셸 명령(`cat`·`sed`·`head`·`rg`·`grep`·`ls`·`find`·`git show`·`git status`·`git diff`)으로 한다. "
              "그것은 위 조항이 금지하는 검사·빌드 명령이 **아니다**. 무엇이든 쓰는 명령(`>`·`>>`·`tee`·`cp`·`mv`·`rm`·`mkdir`·"
              "`git add`·`git commit` 등)과 검증 계획의 검사 명령(`bash scripts/…`·`python3 …`·`unittest`)은 실행하지 않는다."),
    "claude": ("읽기·검색은 `Read`·`Grep`·`Glob` 도구로 한다. 이 실행에는 명령 실행 도구가 없다 — 없는 도구를 요청하지 말고, "
               "그것 없이 판정할 수 없으면 `BLOCKED_CAPABILITY` 로 끝낸다."),
}
READ_MEANS_PREFIX = "읽기 수단: "

MODE_NOTE = {
    "base": "",
    "rerun": ("이 실행은 **검토자만 다시 띄운 것**이다(RUNBOOK §6.6). 구현은 기준 실행 `<evidence-run>` 에서 이미 끝났고 작업 트리는 그때 그대로다.\n"
              "읽을 증거와 구현자 결과 계약은 기준 실행의 것이고, 네 작업 계약만 새 Run `<run-id>` 의 것이다."),
}


def fill(text, values, runtime, mode):
    body = text.split(MARKER, 1)[1] if MARKER in text else text
    body = body.replace("<mode-note>", MODE_NOTE[mode]).replace("<runtime-read-means>", READ_MEANS_PREFIX + READ_MEANS[runtime])
    for key, val in values.items():
        body = body.replace(f"<{key}>", val)
    return body.lstrip("\n")


def problems(filled, mode, values):
    out = []
    left = sorted(set(PLACEHOLDER_RE.findall(filled)))
    if left:
        out.append(f"남은 자리표시자 {left}")
    if "<!--" in filled:
        out.append("HTML 주석이 남아 있다 — 모델에게 그대로 간다")
    n = filled.count(READ_MEANS_PREFIX)
    if n != 1:
        out.append(f"읽기 수단 문장이 {n}개다(정확히 1개여야 한다)")
    if mode == "base" and values["evidence-run"] != values["run-id"]:
        out.append("base 모드인데 evidence-run 이 run-id 와 다르다 — 검토자-only 재실행이면 --mode rerun")
    if not re.fullmatch(r"[0-9a-f]{64}", values["task-sha256"]):
        out.append("task-sha256 이 64자리 16진수가 아니다")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--unit", required=True)
    ap.add_argument("--run", required=True, help="이 실행의 Run id (검토자 계약·출력 경로)")
    ap.add_argument("--evidence-run", help="검토자가 읽을 구현자 증거의 Run id. 생략하면 --run 과 같다(§3 기준 실행)")
    ap.add_argument("--base-sha", required=True, help="검토자 계약 파일의 base_sha 필드 값을 옮겨 적는다")
    ap.add_argument("--task-sha256", required=True, help="검토자 계약 파일의 sha256 (shasum -a 256)")
    ap.add_argument("--runtime", required=True, choices=sorted(READ_MEANS))
    ap.add_argument("--mode", default="base", choices=sorted(MODE_NOTE), help="base=§3 기준 실행 · rerun=§6.6 검토자-only 재실행")
    ap.add_argument("--out", help="쓸 파일. 생략하면 표준 출력")
    ap.add_argument("--template", default=str(TEMPLATE))
    args = ap.parse_args(argv)
    values = {"id": args.unit, "run-id": args.run, "evidence-run": args.evidence_run or args.run,
              "base-sha": args.base_sha, "task-sha256": args.task_sha256}
    filled = fill(Path(args.template).read_text(encoding="utf-8"), values, args.runtime, args.mode)
    bad = problems(filled, args.mode, values)
    if bad:
        for b in bad:
            print(f"FILL_INVALID {b}", file=sys.stderr)
        return 1
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(filled, encoding="utf-8")
        print(f"reviewer-brief → {out} ({len(filled.encode('utf-8'))} bytes · {args.runtime} · {args.mode})")
    else:
        sys.stdout.write(filled)
    return 0


if __name__ == "__main__":
    sys.exit(main())
