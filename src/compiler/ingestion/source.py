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
    """Acquires engineering knowledge from web sources using Firecrawl."""

    def __init__(self, cache_dir: Path = Path("ingestion/cache")):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def acquire(self, source: dict) -> KnowledgeSource | None:
        """Scrape a single source and return structured knowledge."""
        import hashlib
        url = source["url"]
        cache_key = hashlib.md5(url.encode()).hexdigest()
        cache_path = self.cache_dir / f"{cache_key}.json"

        if cache_path.exists():
            import json
            data = json.loads(cache_path.read_text())
            return KnowledgeSource(**data)

        try:
            from firecrawl import FirecrawlApp
            app = FirecrawlApp()
            result = app.scrape_url(url)
            content = result.get("content", "")
            if not content:
                return None
            ks = KnowledgeSource(
                url=url, title=source.get("title", url),
                content=content, domain=source["domain"],
                source_type=source["type"],
                concepts=source.get("concepts", []),
            )
            import json
            cache_path.write_text(json.dumps({
                "url": ks.url, "title": ks.title, "content": ks.content[:50000],
                "domain": ks.domain, "source_type": ks.source_type,
                "concepts": ks.concepts,
            }))
            return ks
        except Exception as e:
            print(f"Failed to acquire {url}: {e}")
            return None

    def acquire_all(self, sources: list[dict] | None = None) -> list[KnowledgeSource]:
        results = []
        for src in (sources or ENGINEERING_SOURCES):
            ks = self.acquire(src)
            if ks:
                results.append(ks)
        return results
