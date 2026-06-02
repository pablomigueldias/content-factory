from app.providers.ollama_client import _parse_facts


def test_parse_plain_array():
    assert _parse_facts('["fato um", "fato dois"]') == ["fato um", "fato dois"]


def test_parse_wrapped_object():
    assert _parse_facts('{"fatos": ["a", "b"]}') == ["a", "b"]


def test_parse_filters_empty():
    assert _parse_facts('["  ", "válido", ""]') == ["válido"]