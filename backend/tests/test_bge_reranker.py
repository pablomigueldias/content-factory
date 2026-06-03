import pytest

from app.providers.bge_reranker import BGEReranker

pytestmark = pytest.mark.integration


def test_reranker_ranks_relevant_fact_highest():
    verifier = BGEReranker()
    claim = "A luz azul é espalhada mais que as outras cores na atmosfera."
    facts = [
        "Gatos ronronam para se comunicar.",
        "O espalhamento de Rayleigh dispersa mais a luz de menor comprimento de onda, como o azul.",
        "A Terra leva 365 dias para orbitar o Sol.",
    ]
    result = verifier.ground(claim, facts)
    assert result.fact_index == 1    
    assert result.verified is True
    assert result.score > 0.5   


def test_reranker_unsupported_claim_not_verified():
    verifier = BGEReranker()
    claim = "Júpiter tem exatamente 79 luas confirmadas."
    facts = [
        "Gatos ronronam para se comunicar.",
        "A fotossíntese converte luz em energia química.",
    ]
    result = verifier.ground(claim, facts)
    assert result.verified is False
    assert result.fact_index is None


def test_reranker_empty_facts():
    result = BGEReranker().ground("qualquer afirmação", [])
    assert result.verified is False
    assert result.fact_index is None
    assert result.score == 0.0