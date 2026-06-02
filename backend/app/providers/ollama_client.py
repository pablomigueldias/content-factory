import json

import ollama

from app.core.config import settings

FACT_EXTRACTION_PROMPT = """Você é um pesquisador. A partir do TEXTO abaixo, extraia \
fatos atômicos, objetivos e verificáveis sobre o tema. Cada fato deve ser uma \
afirmação única e independente, em português.

Regras:
- Extraia entre 5 e 12 fatos.
- Cada fato deve ser autossuficiente (sem "ele", "isso", "esse fenômeno").
- Não invente nada que não esteja no texto.
- Responda APENAS com um array JSON de strings, sem markdown, sem texto extra.

TEXTO:
{text}
"""


def extract_facts(text: str, model: str | None = None) -> list[str]:
    model = model or settings.ollama_model
    client = ollama.Client(host=settings.ollama_base_url)

    response = client.chat(
        model=model,
        messages=[{"role": "user", "content": FACT_EXTRACTION_PROMPT.format(text=text[:6000])}],
        format="json",
        options={"temperature": 0.2},
    )
    content = response["message"]["content"]
    return _parse_facts(content)


def _parse_facts(content: str) -> list[str]:
    data = json.loads(content)
    if isinstance(data, list):
        facts = data
    elif isinstance(data, dict):
        facts = next((v for v in data.values() if isinstance(v, list)), [])
    else:
        facts = []
    return [str(f).strip() for f in facts if str(f).strip()]