"""Markdown frontmatter 파서·직렬화. 키 순서를 보존한다."""
import yaml

FENCE = "---"


def split(text):
    """(frontmatter dict, body str). frontmatter 가 없으면 (None, text)."""
    if not text.startswith(FENCE + "\n"):
        return None, text
    end = text.find("\n" + FENCE + "\n", len(FENCE))
    if end == -1:
        return None, text
    raw = text[len(FENCE) + 1:end]
    body = text[end + len(FENCE) + 2:]
    data = yaml.safe_load(raw) or {}
    return data, body


def join(data, body):
    fm = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_flow_style=None, width=100).rstrip("\n")
    return f"{FENCE}\n{fm}\n{FENCE}\n{body}"


def read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return split(fh.read())


def write(path, data, body):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(join(data, body))
