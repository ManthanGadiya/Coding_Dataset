"""Global constants, enums, limits.

Source: compiler/00_core/07_global_constants.toon
"""

import enum


class Priority(enum.IntEnum):
    P0 = 0
    P1 = 1
    P2 = 2
    P3 = 3
    P4 = 4


class Severity(enum.IntEnum):
    S0 = 0
    S1 = 1
    S2 = 2
    S3 = 3
    S4 = 4


class Risk(enum.IntEnum):
    R0 = 0
    R1 = 1
    R2 = 2
    R3 = 3
    R4 = 4


class Confidence(enum.IntEnum):
    C0 = 0
    C1 = 1
    C2 = 2
    C3 = 3
    C4 = 4


class Quality(enum.IntEnum):
    Q0 = 0
    Q1 = 1
    Q2 = 2
    Q3 = 3
    Q4 = 4
    Q5 = 5


class Complexity(enum.IntEnum):
    X0 = 0
    X1 = 1
    X2 = 2
    X3 = 3
    X4 = 4


class Difficulty(enum.IntEnum):
    D0 = 0
    D1 = 1
    D2 = 2
    D3 = 3
    D4 = 4
    D5 = 5
    D6 = 6


class CapabilityLevel(enum.IntEnum):
    L0 = 0
    L1 = 1
    L2 = 2
    L3 = 3
    L4 = 4
    L5 = 5
    L6 = 6


class ExecutionMode(enum.Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"
    BENCHMARK = "benchmark"
    RESEARCH = "research"


class ExecutionStrategy(enum.Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    DISTRIBUTED = "distributed"
    INCREMENTAL = "incremental"


class LifecycleStage(enum.Enum):
    DISCOVERY = "discovery"
    ACQUISITION = "acquisition"
    NORMALIZATION = "normalization"
    CLASSIFICATION = "classification"
    ONTOLOGY_MAPPING = "ontology_mapping"
    RELATIONSHIP_CONSTRUCTION = "relationship_construction"
    COGNITION_ENRICHMENT = "cognition_enrichment"
    WORLD_INTEGRATION = "world_integration"
    EPISODE_GENERATION = "episode_generation"
    EKR_CREATION = "ekr_creation"
    INTERNAL_REVIEW = "internal_review"
    REPAIR = "repair"
    VALIDATION = "validation"
    QUALITY_ASSESSMENT = "quality_assessment"
    OPTIMIZATION = "optimization"
    SERIALIZATION = "serialization"
    DATASET_INTEGRATION = "dataset_integration"
    RELEASE = "release"
    MONITORING = "monitoring"
    EVOLUTION = "evolution"


class PipelineStage(enum.Enum):
    INITIALIZATION = "initialization"
    KNOWLEDGE_ACQUISITION = "knowledge_acquisition"
    KNOWLEDGE_PARSING = "knowledge_parsing"
    ONTOLOGY_MAPPING = "ontology_mapping"
    KNOWLEDGE_GRAPH_CONSTRUCTION = "knowledge_graph_construction"
    COGNITION_ENRICHMENT = "cognition_enrichment"
    CURRICULUM_PLANNING = "curriculum_planning"
    WORLD_GENERATION = "world_generation"
    EPISODE_GENERATION = "episode_generation"
    EKR_GENERATION = "ekr_generation"
    ARTIFACT_GENERATION = "artifact_generation"
    REPAIR = "repair"
    QUALITY_ANALYSIS = "quality_analysis"
    VALIDATION = "validation"
    OPTIMIZATION = "optimization"
    SERIALIZATION = "serialization"
    RELEASE = "release"


# Global limits
MINIMUM_QUALITY = Quality.Q2
RELEASE_QUALITY = Quality.Q4
MINIMUM_CONFIDENCE = Confidence.C2
GRAPH_CYCLES_FORBIDDEN = True
ORPHAN_NODES_FORBIDDEN = True
IDENTIFIER_FORMAT = "{prefix}-{domain}-{uuid}"
