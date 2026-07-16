"""Domain model — engineering knowledge taxonomy.

Source: compiler/01_ontology/01_taxonomy.toon, compiler/01_ontology/04_domains.toon
"""

from dataclasses import dataclass, field
from enum import Enum


class DomainName(Enum):
    FOUNDATIONS = "Foundations"
    PROGRAMMING = "Programming"
    ALGORITHMS = "Algorithms"
    DATA_STRUCTURES = "Data_Structures"
    SYSTEMS = "Systems"
    COMPILERS = "Compilers"
    NETWORKING = "Networking"
    DATABASES = "Databases"
    DISTRIBUTED_SYSTEMS = "Distributed_Systems"
    SECURITY = "Security"
    SOFTWARE_ARCHITECTURE = "Software_Architecture"
    TESTING = "Testing"
    DEVOPS = "DevOps"
    PERFORMANCE = "Performance"
    CLOUD = "Cloud"
    AI_ENGINEERING = "AI_Engineering"
    HUMAN_FACTORS = "Human_Factors"
    PRODUCTION_ENGINEERING = "Production_Engineering"


DOMAIN_DEPS: dict[DomainName, list[DomainName]] = {
    DomainName.FOUNDATIONS: [],
    DomainName.PROGRAMMING: [DomainName.FOUNDATIONS],
    DomainName.ALGORITHMS: [DomainName.FOUNDATIONS],
    DomainName.DATA_STRUCTURES: [DomainName.ALGORITHMS],
    DomainName.SYSTEMS: [DomainName.PROGRAMMING],
    DomainName.COMPILERS: [DomainName.PROGRAMMING, DomainName.SYSTEMS],
    DomainName.NETWORKING: [DomainName.SYSTEMS],
    DomainName.DATABASES: [DomainName.SYSTEMS],
    DomainName.DISTRIBUTED_SYSTEMS: [DomainName.NETWORKING, DomainName.SYSTEMS],
    DomainName.SECURITY: [DomainName.PROGRAMMING, DomainName.NETWORKING],
    DomainName.SOFTWARE_ARCHITECTURE: [DomainName.PROGRAMMING, DomainName.DISTRIBUTED_SYSTEMS],
    DomainName.TESTING: [DomainName.PROGRAMMING],
    DomainName.DEVOPS: [DomainName.SYSTEMS, DomainName.DISTRIBUTED_SYSTEMS],
    DomainName.PERFORMANCE: [DomainName.SYSTEMS, DomainName.ALGORITHMS],
    DomainName.CLOUD: [DomainName.DISTRIBUTED_SYSTEMS, DomainName.NETWORKING],
    DomainName.AI_ENGINEERING: [DomainName.PROGRAMMING, DomainName.DISTRIBUTED_SYSTEMS],
    DomainName.HUMAN_FACTORS: [],
    DomainName.PRODUCTION_ENGINEERING: [DomainName.DEVOPS, DomainName.DISTRIBUTED_SYSTEMS],
}


@dataclass
class Domain:
    name: DomainName
    purpose: str = ""
    concepts: list[str] = field(default_factory=list)
    dependencies: list[DomainName] = field(default_factory=list)

    @classmethod
    def all(cls) -> list["Domain"]:
        return [cls(name=n, dependencies=DOMAIN_DEPS.get(n, [])) for n in DomainName]
