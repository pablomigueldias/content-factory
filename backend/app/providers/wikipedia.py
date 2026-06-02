from dataclasses import dataclass
from urllib.parse import quote
import uuid

from app.models.source import Source, SourceType

import httpx

WIKIPEDIA_API = "https://pt.wikipedia.org/w/api.php"
WIKIPEDIA_BASE = "https://pt.wikipedia.org/wiki/"

USER_AGENT = "ContentFactory/0.1 (content research; contato@exemplo.com)"


@dataclass
class WikipediaResult:
    title: str
    url: str
    raw_content: str


def search_wikipedia(query: str, client: httpx.Client | None = None) -> WikipediaResult | None:

    owns_client = client is None
    client = client or httpx.Client(timeout=10.0, headers={"User-Agent": USER_AGENT})
    try:

        search = client.get(
            WIKIPEDIA_API,
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": 1,
                "format": "json",
            },
        )
        search.raise_for_status()
        hits = search.json()["query"]["search"]
        if not hits:
            return None
        title = hits[0]["title"]

        extract = client.get(
            WIKIPEDIA_API,
            params={
                "action": "query",
                "prop": "extracts",
                "explaintext": 1,
                "redirects": 1,
                "titles": title,
                "format": "json",
            },
        )
        extract.raise_for_status()
        pages = extract.json()["query"]["pages"]
        page = next(iter(pages.values()))
        raw_content = page.get("extract", "")

        url = WIKIPEDIA_BASE + quote(title.replace(" ", "_"))
        return WikipediaResult(title=title, url=url, raw_content=raw_content)
    finally:
        if owns_client:
            client.close()


def result_to_source(result: WikipediaResult, job_id: uuid.UUID) -> Source:
    return Source(
        job_id=job_id,
        source_type=SourceType.WIKIPEDIA,
        title=result.title,
        url=result.url,
        raw_content=result.raw_content,
        reliability=80,
    )