import datetime as _dt
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

import yaml

from . import HARNESS_ROOT


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def dump_yaml(data):
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False, width=100)


def load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_any(path):
    path = Path(path)
    if path.suffix.lower() == ".json":
        return load_json(path)
    return load_yaml(path)


def today():
    return _dt.date.today().isoformat()


def now_iso():
    return _dt.datetime.now(_dt.timezone.utc).astimezone().replace(microsecond=0).isoformat()


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def project_root(start=None):
    """git 최상위를 프로젝트 루트로 본다. git 밖이면 cwd."""
    start = Path(start or os.getcwd()).resolve()
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=str(start), capture_output=True, text=True, check=True)
        return Path(out.stdout.strip())
    except Exception:
        return start


_SECRET_PATTERNS = [
    (re.compile(r"(?i)(api[_-]?key|token|secret|password|passwd|bearer|authorization)\s*[=:]\s*\S+"), r"\1=<masked>"),
    # 접두사 뒤에 **구분자**를 요구한다. 실제 토큰은 전부 그 형태다 — `sk-…` · `ghp_…` · `xoxb-…`.
    # 구분자를 요구하지 않으면 `skills-before` 같은 평범한 파일명이 토큰으로 잡힌다. 그것이 왜 문제냐면
    # 마스킹된 문자열이 증거의 `command` 로 저장되는데(evidence.py), 종료 검사는 검증 계획의 **원문**으로
    # 정확 조회하므로(close.py) 실제로 exit 0 인 검사가 "evidence 에 명령 없음" 으로 떨어진다.
    # 2026-08-31 run_6165c4796868 이 이것으로 막혔다 — 오탐은 조용하지 않고 완료를 막는다.
    (re.compile(r"\b(sk|ghp|gho|ghu|ghs|xoxb|xoxp)[-_][A-Za-z0-9_\-]{10,}\b"), "<masked-token>"),
    # AWS 액세스 키만 구분자가 없다. 대문자·숫자로만 이뤄진 고정 길이라 따로 둔다.
    (re.compile(r"\bAKIA[0-9A-Z]{12,}\b"), "<masked-token>"),
]


def mask_secrets(text):
    for pat, rep in _SECRET_PATTERNS:
        text = pat.sub(rep, text)
    return text


def rel(path, root):
    try:
        return str(Path(path).resolve().relative_to(Path(root).resolve()))
    except ValueError:
        return str(path)
