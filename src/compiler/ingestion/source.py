"""Source ingestion — fetches real engineering knowledge from web sources.

Uses Firecrawl to scrape engineering documentation, RFCs, design patterns,
incident postmortems, and standards. Feeds extracted knowledge into the
compiler's domain ontology for enriched generation.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class KnowledgeSource:
    url: str
    title: str
    content: str
    domain: str
    source_type: str  # article, rfc, docs, pattern, postmortem
    concepts: list[str] = field(default_factory=list)


ENGINEERING_SOURCES: list[dict] = [
    {
        "url": "https://www.systemdesignhandbook.com/blog/large-scale-distributed-systems/",
        "domain": "Distributed_Systems",
        "type": "article",
        "concepts": ["CAP theorem", "sharding", "replication", "consensus", "fault tolerance"],
    },
    {
        "url": "https://refactoring.guru/design-patterns/catalog",
        "domain": "Software_Architecture",
        "type": "pattern",
        "concepts": ["Singleton", "Factory", "Observer", "Strategy", "Decorator"],
    },
    {
        "url": "https://incident.io/blog/best-incident-postmortem-software-2026-guide",
        "domain": "Production_Engineering",
        "type": "postmortem",
        "concepts": ["incident response", "postmortem", "SRE", "blameless culture"],
    },
    {
        "url": "https://www.ietf.org/process/rfcs/",
        "domain": "Networking",
        "type": "rfc",
        "concepts": ["RFC", "specification", "standards", "protocol"],
    },
    {
        "url": "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7",
        "domain": "Software_Architecture",
        "type": "article",
        "concepts": ["system design", "architecture", "scalability", "trade-offs"],
    },
]


class SourceAcquirer:
    """Acquires engineering knowledge from web sources using Firecrawl.

    Three acquisition modes (tried in order):
      1. Firecrawl Python SDK (if installed and configured)
      2. Direct HTTP fetch with requests
      3. Read from a pre-seeded file (ingestion/ingest/ directory)
    """

    def __init__(self, cache_dir: Path = Path("ingestion/cache"),
                 ingest_dir: Path = Path("ingestion/ingest")):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ingest_dir = ingest_dir
        self.ingest_dir.mkdir(parents=True, exist_ok=True)

    def acquire(self, source: dict) -> KnowledgeSource | None:
        """Scrape a single source and return structured knowledge."""
        import hashlib
        import json
        url = source["url"]
        cache_key = hashlib.md5(url.encode()).hexdigest()
        cache_path = self.cache_dir / f"{cache_key}.json"

        if cache_path.exists():
            data = json.loads(cache_path.read_text())
            return KnowledgeSource(**data)

        result = self._try_firecrawl(source) or self._try_http(source) or self._try_ingest_file(source)
        if result is None:
            return None

        cache_path.write_text(json.dumps({
            "url": result.url, "title": result.title,
            "content": result.content[:50000],
            "domain": result.domain, "source_type": result.source_type,
            "concepts": result.concepts,
        }))
        return result

    def _try_firecrawl(self, source: dict) -> KnowledgeSource | None:
        try:
            from firecrawl import FirecrawlApp
            app = FirecrawlApp()
            result = app.scrape_url(source["url"])
            content = result.get("content", "")
            if not content:
                return None
            return KnowledgeSource(
                url=source["url"], title=source.get("title", source["url"]),
                content=content, domain=source["domain"],
                source_type=source["type"],
                concepts=source.get("concepts", []),
            )
        except Exception:
            return None

    def _try_http(self, source: dict) -> KnowledgeSource | None:
        try:
            import requests
            resp = requests.get(source["url"], timeout=15)
            resp.raise_for_status()
            content = resp.text
            return KnowledgeSource(
                url=source["url"], title=source.get("title", source["url"]),
                content=content[:50000], domain=source["domain"],
                source_type=source["type"],
                concepts=source.get("concepts", []),
            )
        except Exception:
            return None

    def _try_ingest_file(self, source: dict) -> KnowledgeSource | None:
        import hashlib
        import json
        import re
        name = re.sub(r'[^a-zA-Z0-9]+', '_', source["url"].split("//")[-1].split("/")[0])
        for f in self.ingest_dir.glob(f"*{name}*"):
            try:
                return KnowledgeSource(
                    url=source["url"], title=source.get("title", source["url"]),
                    content=f.read_text(encoding="utf-8")[:50000],
                    domain=source["domain"], source_type=source["type"],
                    concepts=source.get("concepts", []),
                )
            except Exception:
                continue
        return None

    def acquire_all(self, sources: list[dict] | None = None) -> list[KnowledgeSource]:
        results = []
        for src in (sources if sources is not None else ENGINEERING_SOURCES):
            ks = self.acquire(src)
            if ks:
                results.append(ks)
        return results
