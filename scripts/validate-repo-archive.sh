#!/usr/bin/env bash
set -euo pipefail

archive_dir=${1:?"usage: validate-repo-archive.sh <archive-dir>"}

# rg(ripgrep) 가 정식 설치가 아닌 환경(앱 번들 바이너리만 있거나 Orca 워커 셸)에서도 같은 검사를 하도록
# grep -E 로 폴백한다. 두 패턴은 ERE 범위 안이라 판정이 같다. (T0 chg-20260827-rg-fallback-validate)
if command -v rg >/dev/null 2>&1; then
  matches() { rg -q "$1" "$2"; }
else
  matches() { grep -Eq "$1" "$2"; }
fi

required_files=(
  "_source.md"
  "00-exploration.md"
  "02-workflow-summary.md"
  "04-components-table.md"
  "05-pm-harness-notes.md"
  "06-source-evidence.md"
)

required_dirs=("01-docs" "03-components")

if [[ ! -d "$archive_dir" ]]; then
  printf 'FAIL: archive directory does not exist: %s\n' "$archive_dir" >&2
  exit 1
fi

for relative_path in "${required_files[@]}"; do
  if [[ ! -s "$archive_dir/$relative_path" ]]; then
    printf 'FAIL: required non-empty file is missing: %s\n' "$relative_path" >&2
    exit 1
  fi
done

for relative_path in "${required_dirs[@]}"; do
  if [[ ! -d "$archive_dir/$relative_path" ]]; then
    printf 'FAIL: required directory is missing: %s\n' "$relative_path" >&2
    exit 1
  fi
done

if ! matches '^[-*] Commit SHA: `[0-9a-f]{40}`$|^[-*] Commit SHA: [0-9a-f]{40}$' "$archive_dir/_source.md"; then
  printf 'FAIL: _source.md does not contain a 40-character Commit SHA field\n' >&2
  exit 1
fi

if ! matches '원문 위치|Source location|source location' "$archive_dir/04-components-table.md"; then
  printf 'FAIL: 04-components-table.md has no source-location column\n' >&2
  exit 1
fi

printf 'PASS: %s\n' "$archive_dir"
