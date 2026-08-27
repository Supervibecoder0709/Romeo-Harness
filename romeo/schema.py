"""JSON Schema 부분집합 검증기(표준 라이브러리만). type·required·properties·additionalProperties·enum·items·
pattern·minLength·minItems·const·$ref(#/definitions/...)를 지원한다. 오류는 경로와 함께 목록으로 돌려준다."""
import re

_TYPES = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "array": list,
    "object": dict,
    "null": type(None),
}


def _is_type(value, t):
    if t == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if t == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if t == "boolean":
        return isinstance(value, bool)
    return isinstance(value, _TYPES[t])


def _resolve(ref, root):
    assert ref.startswith("#/"), ref
    node = root
    for part in ref[2:].split("/"):
        node = node[part]
    return node


def validate(instance, schema, root=None, path="$"):
    root = root if root is not None else schema
    errors = []
    if "$ref" in schema:
        return validate(instance, _resolve(schema["$ref"], root), root, path)
    t = schema.get("type")
    if t is not None:
        types = t if isinstance(t, list) else [t]
        if not any(_is_type(instance, x) for x in types):
            errors.append(f"{path}: 타입이 {types} 여야 하는데 {type(instance).__name__}")
            return errors
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} 는 허용값 {schema['enum']} 에 없음")
    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: {instance!r} != {schema['const']!r}")
    if isinstance(instance, str):
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append(f"{path}: {instance!r} 가 패턴 {schema['pattern']} 과 맞지 않음")
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: 길이 {len(instance)} < minLength {schema['minLength']}")
    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: 항목 {len(instance)} < minItems {schema['minItems']}")
        if "items" in schema:
            for i, item in enumerate(instance):
                errors.extend(validate(item, schema["items"], root, f"{path}[{i}]"))
    if isinstance(instance, dict):
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}: 필수 키 {key!r} 없음")
        for key, value in instance.items():
            if key in props:
                errors.extend(validate(value, props[key], root, f"{path}.{key}"))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}: 허용되지 않은 키 {key!r}")
    for alt_key in ("anyOf", "oneOf"):
        if alt_key in schema:
            ok = any(not validate(instance, alt, root, path) for alt in schema[alt_key])
            if not ok:
                errors.append(f"{path}: {alt_key} 중 어느 것도 맞지 않음")
    return errors
