"""하네스 지표 정의 **정본**과 집계. `romeo metrics` 가 이것을 돌아 표를 인쇄한다.

## 왜 정본이 여기 있나

지표는 이름·읽는 자리·사건 규칙이 한 자리에 있어야 대조가 성립한다. 출력이 정본을 돌아 만들어지고
검사가 정본을 import 해 대조하면, 「출력에 있는데 정의되지 않은 행」도 「정의됐는데 인쇄되지 않는 행」도
생기지 않는다. 이름과 개수를 검사에 옮겨 적으면 그 사본이 곧 두 번째 정본이 되고, 정본이 바뀌어도
검사는 옛 목록을 계속 덮는다.

## 관측 사건 — 무엇을 세는가

**관측 사건은 그 값을 계산하는 데 필요한 자리가 다 채워진 기록만 센다.** 자리가 비어 있는 기록은 사건이 아니다.
`routing.history` 에 들어 있는 `{}` 는 재분류 사건이 아니고, `closed_at` 이 비어 있는 T0 단위는 처리 시간 표본이 아니다.
이 규칙이 없으면 「기록할 자리는 있는데 아무도 쓰지 않는다」가 「0 이다」로 인쇄된다.

**키가 있다는 것과 값이 채워졌다는 것은 다르다.** `{"unit": null}` 은 키를 갖고도 무엇으로 재분류했는지
말하지 않으므로 사건이 아니다 — `{}` 만 걸러내는 판별은 그 기록을 사건으로 흘려보내고, 그런 기록 하나로
미집계가 숫자로 바뀐다. 그래서 판별은 truthiness 가 아니라 `_is_filled` 한 자리에서 한다:
truthiness 로 보면 값이 전부 빈 컨테이너가 채워진 것으로 새고, 값인 `0` 과 `False` 는 빈 자리로 세진다.

`needs_event` 가 참인 지표는 **사건이 0 이면 숫자를 주장하지 않는다** — 값 자리에 `미집계` 와
**관측한 사실만** 담은 사유를 인쇄한다. 「기록이 없다」는 관측이지만 「그런 일이 없었다」는 관측이 아니다.
`gate-miss` 만 거짓인 이유: 그 값은 **대상 범위를 전부 읽고 센 건수**라 0 이 그 자체로 관측이다.
나머지 셋은 사건을 분모나 표본으로 쓰므로 사건이 0 이면 값이 정의되지 않는다.

## 출처

각 지표는 값과 함께 **대상 범위**(어떤 파일을 읽는가) · **읽은 파일 수** · **읽는 자리**(필드·키 이름) ·
**사건이 발견된 파일과 그 파일에서 읽은 값**을 인쇄한다. 「T0 처리 시간 70초」가 어느 파일의 어느 두 시각을
뺀 것인지 인쇄되지 않으면 그 숫자는 손으로 다시 셀 수 없고, 다시 셀 수 없는 숫자는 믿는 수밖에 없다(K-63).
"""
import statistics
from datetime import datetime
from pathlib import Path

from .frontmatter import read as read_frontmatter
from .util import load_yaml

#: 사건이 없어 값을 주장하지 않을 때 값 자리에 인쇄하는 말.
UNCOUNTED = "미집계"

FIXTURE_GLOB = "fixtures/requests/*.yaml"
SPEC_GLOB = "docs/work/*/spec.md"


class Metric:
    """지표 하나의 정의. 값은 담지 않는다 — `collect()` 가 그때그때 읽는다."""

    def __init__(self, id, name, unit_label, scope_glob, read_at, event_rule, needs_event, collect):
        self.id = id
        self.name = name              #: 인쇄 이름. charter 가 이름 붙인 것과 같아야 한다
        self.unit_label = unit_label  #: 값의 단위 — 표에 그대로 붙는다
        self.scope_glob = scope_glob  #: 대상 범위. 저장소 루트 기준 glob
        self.read_at = read_at        #: 읽는 자리 — 필드·키 이름
        self.event_rule = event_rule  #: 무엇을 관측 사건으로 세는가
        self.needs_event = needs_event
        self._collect = collect

    def __repr__(self):
        return f"<Metric {self.id}>"


class Reading:
    """한 지표를 한 트리에서 읽은 결과."""

    def __init__(self, metric, value_text, events, scanned, event_rows, breakdown, reason=None):
        self.metric = metric
        self.value_text = value_text    #: 표의 값 자리에 서는 문자열 (`미집계` 이거나 단위가 붙은 숫자)
        self.events = events            #: 관측 사건 수
        self.scanned = scanned          #: 대상 범위에서 실제로 읽은 파일 수
        self.event_rows = event_rows    #: [(저장소 루트 기준 상대 경로, 그 파일에서 읽은 값)]
        self.breakdown = breakdown      #: 값이 어떻게 나왔는지 — 분자·분모·표본
        self.reason = reason            #: 미집계 사유. 관측한 것만 담는다

    def __repr__(self):
        return f"<Reading {self.metric.id}={self.value_text}>"


# --- 읽기 도우미 -----------------------------------------------------------------

def _paths(root, glob):
    return sorted(Path(root).glob(glob))


def _rel(root, path):
    return str(Path(path).relative_to(Path(root)))


def _is_filled(value):
    """이 자리가 **무언가를 말하는가**. 사건 판별은 전부 이 함수를 지난다.

    빈 자리: `None` · 공백뿐인 문자열 · 항목이 없거나 항목이 전부 빈 컨테이너(`{}` · `[]` ·
    `{"unit": None}` · `[{}]`). 채워진 자리: 그 밖의 값 — `0` 과 `False` 도 값이므로 채워진 것으로 센다.
    컨테이너는 **일부라도 말하면** 말하는 것으로 본다(`{"unit": "T1", "note": None}` 은 무엇으로
    재분류했는지 말한다). 모든 키가 채워질 것을 요구하면 `changes: []` 처럼 빈 목록이 곧 값인 기록이
    사건에서 빠지므로, 그 방향은 같은 결함을 반대쪽으로 만든다.
    """
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, dict):
        return any(_is_filled(v) for v in value.values())
    if isinstance(value, (list, tuple, set)):
        return any(_is_filled(v) for v in value)
    return True


def _parse_time(value):
    """frontmatter 의 시각. YAML 이 문자열로 주기도 datetime 으로 주기도 한다."""
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    return parsed


def _seconds(value):
    """초를 인쇄용 문자열로. 정수면 소수점을 붙이지 않는다."""
    return f"{int(value)}초" if float(value).is_integer() else f"{value:.1f}초"


def _rate(part, whole):
    return f"{(part / whole) * 100:.1f}%"


def _read_specs(root):
    """(경로, frontmatter) 목록. frontmatter 가 없는 파일도 읽은 파일로는 센다."""
    out = []
    for path in _paths(root, SPEC_GLOB):
        try:
            fm, _body = read_frontmatter(path)
        except Exception:  # noqa: BLE001 — 읽히지 않는 문서는 사건이 아니다. 집계를 멈추지 않는다(AC-5)
            fm = None
        out.append((path, fm or {}))
    return out


def _read_fixtures(root):
    out = []
    for path in _paths(root, FIXTURE_GLOB):
        try:
            data = load_yaml(path) or {}
        except Exception:  # noqa: BLE001
            data = {}
        out.append((path, data))
    return out


# --- 집계 ------------------------------------------------------------------------

def _classification_correction(metric, root):
    """분류 수정률 — 사람이 분류를 검토한 기록 중 **고친** 비율.

    사건은 `human_correction.verdict` 가 채워진 기록이다. `human_correction` 이 없는 fixture 는
    사람이 본 적이 없다는 뜻이지 「고치지 않았다」가 아니므로 분모에 들어가지 않는다 —
    그것을 분모에 넣으면 검토율이 수정률의 이름으로 인쇄된다.

    필요한 자리는 `verdict` 하나다. 채워졌는지는 `_is_filled` 로 본다 — 공백뿐인 문자열이나
    값이 전부 빈 컨테이너가 verdict 자리에 있으면 사람이 무엇으로 판정했는지 말하지 않는다.
    `human_correction` 의 다른 키(`changes: []` 등)는 이 값을 계산하는 데 필요한 자리가 아니므로 보지 않는다.
    """
    files = _read_fixtures(root)
    rows, verdicts = [], {}
    for path, data in files:
        hc = data.get("human_correction")
        if not isinstance(hc, dict):
            continue
        verdict = hc.get("verdict")
        if not _is_filled(verdict):
            continue
        rows.append((_rel(root, path), f"human_correction.verdict={verdict}"))
        verdicts[verdict] = verdicts.get(verdict, 0) + 1
    events = len(rows)
    corrected = verdicts.get("corrected", 0)
    tally = " · ".join(f"{k} {v}" for k, v in sorted(verdicts.items())) or "없음"
    if events == 0:
        return Reading(metric, UNCOUNTED, 0, len(files), rows,
                       f"verdict 가 채워진 검토 기록 0건 · verdict 분포: {tally}",
                       reason=f"관측 사건 0건 — {metric.scope_glob} {len(files)}건을 읽었고 "
                              f"{metric.read_at} 가 채워진 기록이 하나도 없다")
    return Reading(metric, _rate(corrected, events), events, len(files), rows,
                   f"corrected {corrected} / verdict 기록 {events} · verdict 분포: {tally}")


def _gate_miss(metric, root):
    """gate 누락 — 라우터가 힌트한 hard gate 를 fixture 가 체크하지 않은 건수.

    세는 것은 `romeo.fixtures.run_report` 다(고치지 않는다). 여기서는 그 판정이 걸린 fixture 의
    경로와 그 fixture 에서 읽은 미체크 게이트만 다시 인쇄한다.
    """
    from .fixtures import load_fixtures, run_report
    from .policy import RouteError, load_policy, route

    directory = Path(root) / "fixtures" / "requests"
    files = _paths(root, FIXTURE_GLOB)
    if not directory.is_dir() or not files:
        return Reading(metric, "0건", 0, 0, [], "읽은 fixture 0건",
                       reason=None)
    fixtures = load_fixtures(directory)
    report = run_report(fixtures)
    by_id = {f["id"]: f for f in fixtures}
    rows = []
    policy = load_policy()
    for row in report["rows"]:
        if not row["gate_miss"]:
            continue
        fixture = by_id.get(row["id"], {})
        try:
            unchecked = route(fixture["classification"], policy)["gate_hints"]["unchecked"]
        except (RouteError, KeyError):
            unchecked = []
        rows.append((_rel(root, fixture["_path"]),
                     f"gate_hints.unchecked={unchecked} · classification.gates={fixture['classification'].get('gates')}"))
    return Reading(metric, f"{len(rows)}건", len(rows), len(files), rows,
                   f"gate 누락 {len(rows)} / route 를 통과시킨 fixture {report['total']}")


def _t0_lead_time(metric, root):
    """T0 처리 시간 — `unit: T0` 인 작업 단위의 승인→종료 중앙값.

    표본은 `approved_at` 과 `closed_at` 이 **둘 다** 채워진 T0 단위다. 하나가 비면 시간을 뺄 수 없으므로
    표본이 아니다 — 그것을 0 초로 세면 열려 있는 단위가 중앙값을 끌어내린다.
    """
    specs = _read_specs(root)
    rows, samples = [], []
    for path, fm in specs:
        if fm.get("unit") != "T0":
            continue
        opened, closed = _parse_time(fm.get("approved_at")), _parse_time(fm.get("closed_at"))
        if opened is None or closed is None:
            continue
        seconds = (closed - opened).total_seconds()
        samples.append(seconds)
        rows.append((_rel(root, path),
                     f"unit=T0 · approved_at={fm.get('approved_at')} · closed_at={fm.get('closed_at')} "
                     f"→ {_seconds(seconds)}"))
    t0_total = sum(1 for _p, fm in specs if fm.get("unit") == "T0")
    if not samples:
        return Reading(metric, UNCOUNTED, 0, len(specs), rows,
                       f"승인·종료 시각이 둘 다 채워진 T0 단위 0건 / T0 단위 {t0_total}",
                       reason=f"관측 사건 0건 — {metric.scope_glob} {len(specs)}건을 읽었고 "
                              f"{metric.read_at} 가 둘 다 채워진 T0 단위가 하나도 없다")
    return Reading(metric, f"중앙값 {_seconds(statistics.median(samples))}", len(samples), len(specs), rows,
                   f"표본 {len(samples)} / T0 단위 {t0_total} · 최소 {_seconds(min(samples))} · "
                   f"최대 {_seconds(max(samples))}")


def _reclassification(metric, root):
    """재분류율 — `routing.history` 에 재분류 기록이 남은 작업 단위의 비율.

    사건은 **내용이 채워진** history 항목이다. 빈 항목(`{}`)도, 키만 있고 값이 전부 비어 있는 항목
    (`{"unit": null}`)도 무엇으로 재분류했는지 말하지 않으므로 사건이 아니다 — 키의 존재가 아니라
    `_is_filled` 로 내용을 본다. 사건이 0 이면 값을 주장하지 않는다 — 이 자리에 `0%` 를 인쇄하면
    「재분류가 없었다」와 「일어나도 기록되지 않는다」가 구별되지 않는다.
    """
    specs = _read_specs(root)
    rows = []
    for path, fm in specs:
        history = ((fm.get("routing") or {}).get("history")) or []
        if not isinstance(history, list):
            continue
        filled = [i for i, entry in enumerate(history) if isinstance(entry, dict) and _is_filled(entry)]
        if not filled:
            continue
        rows.append((_rel(root, path),
                     "routing.history[" + ", ".join(str(i) for i in filled) + "] — "
                     + "; ".join(str(sorted((history[i] or {}).keys())) for i in filled)))
    events = len(rows)
    empty_slots = sum(1 for _p, fm in specs
                      if isinstance(((fm.get("routing") or {}).get("history")) or [], list)
                      and any(not (isinstance(e, dict) and _is_filled(e))
                              for e in (((fm.get("routing") or {}).get("history")) or [])))
    if events == 0 or not specs:
        return Reading(metric, UNCOUNTED, 0, len(specs), rows,
                       f"채워진 routing.history 항목이 있는 단위 0건 / 읽은 단위 {len(specs)} "
                       f"(빈 항목만 가진 단위 {empty_slots})",
                       reason=f"관측 사건 0건 — {metric.scope_glob} {len(specs)}건을 읽었고 "
                              f"{metric.read_at} 에 내용이 채워진 항목이 하나도 없다")
    return Reading(metric, _rate(events, len(specs)), events, len(specs), rows,
                   f"재분류 기록이 있는 단위 {events} / 읽은 단위 {len(specs)}")


#: **정본.** 인쇄되는 행도, 검사가 대조하는 목록도 전부 여기서 나온다.
METRICS = (
    Metric(
        id="classification-correction-rate",
        name="분류 수정률",
        unit_label="%",
        scope_glob=FIXTURE_GLOB,
        read_at="human_correction.verdict",
        event_rule="verdict 가 채워진 사람 검토 기록 1건 = 사건 1건. human_correction 이 비어 있으면 사건이 아니다",
        needs_event=True,
        collect=_classification_correction,
    ),
    Metric(
        id="gate-miss",
        name="gate 누락",
        unit_label="건",
        scope_glob=FIXTURE_GLOB,
        read_at="classification.gates · route() 의 gate_hints.unchecked",
        event_rule="라우터가 힌트한 hard gate 를 체크하지 않은 fixture 1건 = 사건 1건",
        needs_event=False,
        collect=_gate_miss,
    ),
    Metric(
        id="t0-lead-time",
        name="T0 처리 시간",
        unit_label="초",
        scope_glob=SPEC_GLOB,
        read_at="unit · approved_at · closed_at",
        event_rule="approved_at 과 closed_at 이 둘 다 채워진 T0 단위 1건 = 표본 1건",
        needs_event=True,
        collect=_t0_lead_time,
    ),
    Metric(
        id="reclassification-rate",
        name="재분류율",
        unit_label="%",
        scope_glob=SPEC_GLOB,
        read_at="routing.history",
        event_rule="내용이 채워진 routing.history 항목을 가진 단위 1건 = 사건 1건. 빈 항목도, 키만 있고 값이 전부 빈 항목도 사건이 아니다",
        needs_event=True,
        collect=_reclassification,
    ),
)


def collect(root):
    """정본을 돌아 한 트리의 지표를 전부 읽는다. 값 때문에 예외를 올리지 않는다."""
    root = Path(root)
    return [m._collect(m, root) for m in METRICS]


# --- 인쇄 ------------------------------------------------------------------------

def format_report(readings, root=None):
    lines = []
    if root is not None:
        lines.append(f"romeo metrics · root {root} · 지표 {len(readings)}건")
        lines.append("")
    lines.append("| 지표 | 값 | 관측 사건 | 읽은 파일 | 읽는 자리 |")
    lines.append("| --- | --- | --- | --- | --- |")
    for r in readings:
        lines.append(f"| {r.metric.name} | {r.value_text} | {r.events}건 | {r.scanned}건 "
                     f"| {r.metric.scope_glob} → {r.metric.read_at} |")
    lines.append("")
    lines.append("## 원본 — 이 숫자를 손으로 다시 세려면")
    for r in readings:
        lines.append("")
        lines.append(f"### {r.metric.name} — {r.value_text}")
        lines.append(f"- 대상 범위: {r.metric.scope_glob} · 읽은 파일 {r.scanned}건")
        lines.append(f"- 읽는 자리: {r.metric.read_at}")
        lines.append(f"- 사건 규칙: {r.metric.event_rule}")
        lines.append(f"- 관측 사건: {r.events}건 · 내역: {r.breakdown}")
        if r.reason:
            lines.append(f"- 미집계 사유: {r.reason}")
        if r.event_rows:
            lines.append(f"- 사건이 발견된 파일 ({len(r.event_rows)}건):")
            for path, read in r.event_rows:
                lines.append(f"  - {path} → {read}")
        else:
            lines.append(f"- 사건이 발견된 파일: 없음 — {r.metric.scope_glob} {r.scanned}건을 전부 읽었다")
    return "\n".join(lines)


def report(root):
    """(readings, 인쇄 문자열)."""
    readings = collect(root)
    return readings, format_report(readings, root=root)
