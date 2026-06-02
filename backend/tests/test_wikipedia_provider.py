import uuid

import httpx
import pytest

from app.models.source import SourceType
from app.providers.wikipedia import (
    WikipediaResult,
    result_to_source,
    search_wikipedia,
)


def _mock_client(search_hits: list[dict], extract: str) -> httpx.Client:
    """Client falso: responde busca e extract conforme os params, sem rede."""
    def handler(request: httpx.Request) -> httpx.Response:
        params = request.url.params
        if params.get("list") == "search":
            return httpx.Response(200, json={"query": {"search": search_hits}})
        if params.get("prop") == "extracts":
            return httpx.Response(
                200, json={"query": {"pages": {"42": {"extract": extract}}}}
            )
        return httpx.Response(404)

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_search_returns_result():
    client = _mock_client(
        search_hits=[{"title": "Espalhamento de Rayleigh"}],
        extract="A luz azul é espalhada mais que a vermelha.",
    )
    result = search_wikipedia("por que o céu é azul", client=client)

    assert result is not None
    assert result.title == "Espalhamento de Rayleigh"
    assert "luz azul" in result.raw_content
    assert result.url.endswith("Espalhamento_de_Rayleigh")


def test_search_no_results_returns_none():
    client = _mock_client(search_hits=[], extract="")
    assert search_wikipedia("xyzqualquercoisa", client=client) is None


def test_result_to_source_sets_wikipedia_reliability():
    result = WikipediaResult(
        title="Teste", url="https://pt.wikipedia.org/wiki/Teste", raw_content="conteúdo"
    )
    source = result_to_source(result, job_id=uuid.uuid4())

    assert source.source_type == SourceType.WIKIPEDIA
    assert source.reliability == 80
    assert source.title == "Teste"