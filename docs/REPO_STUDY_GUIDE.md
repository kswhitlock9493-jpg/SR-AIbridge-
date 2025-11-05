# Repository Study Guide - Using Parser, Blueprint, and Truth Engines

## Overview

This guide demonstrates how to use the **Parser Engine**, **Blueprint Engine**, and **Truth Engine** together to perform comprehensive repository analysis. The study script showcases the coordinated capabilities of these three core engines.

## The Three Engines

### 🔍 Parser Engine
**Purpose**: Content ingestion with lineage tracking and provenance

**Capabilities**:
- Multi-format document parsing (Markdown, JSON, YAML, Python, JavaScript)
- Intelligent chunking with paragraph-aware segmentation
- Metadata extraction and tagging
- Full-text search across ingested content
- Lineage tracking for content provenance
- SHA256-based content addressing

**Location**: `bridge_backend/bridge_core/engines/parser/`

### 📋 Blueprint Engine  
**Purpose**: Transform free-form briefs into structured, executable plans

**Capabilities**:
- Derives objectives from natural language descriptions
- Explodes objectives into granular, dependency-aware tasks
- Generates success criteria and acceptance tests
- Identifies agent requirements and role assignments
- Creates task dependency graphs (DAG)
- Produces artifact specifications

**Location**: `bridge_backend/bridge_core/engines/blueprint/`

### ✅ Truth Engine
**Purpose**: Fact certification and state validation with rollback protection

**Capabilities**:
- Validates system state against expected blueprints
- Certifies deployment facts with provenance
- Maintains fact history and audit trail
- Provides rollback protection
- Similarity-based fact deduplication (Jaccard similarity)
- QEH-v3 entropy hashing for verification

**Location**: `bridge_backend/bridge_core/engines/truth/`

## Study Script Usage

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt
```

### Running the Study

```bash
# Execute the comprehensive repository study
python study_repo_with_engines.py
```

### What the Script Does

The script performs a **three-phase analysis** of the SR-AIbridge repository:

#### Phase 1: Parser Engine - Documentation Ingestion
- Ingests key documentation files:
  - `README.md` - Main repository documentation
  - `BLUEPRINT_ENGINE_GUIDE.md` - Blueprint engine guide
  - `ENGINE_CATALOG.md` - Complete engine catalog
  - `DOCUMENTATION_INDEX.md` - Documentation index
  - `SYSTEM_BLUEPRINT.md` - System architecture
- Chunks content into searchable segments
- Tags chunks with metadata
- Enables full-text search across documentation
- Stores results in `vault/parser/`

#### Phase 2: Blueprint Engine - Analysis Planning
- Creates structured analysis plans from natural language briefs
- Generates two blueprints:
  1. **Comprehensive Repository Analysis** - Multi-phase study plan
  2. **Engine Integration Study** - How the three engines work together
- Produces task breakdowns with dependencies
- Identifies success criteria and artifacts

#### Phase 3: Truth Engine - Fact Certification
- Certifies key repository facts with provenance
- Validates facts about:
  - Engine architecture (20 engines in 4 categories)
  - Technology stack (FastAPI, React)
  - Documentation coverage (100,000+ lines)
  - Event bus architecture (33 event topics)
- Deduplicates similar facts using Jaccard similarity
- Stores certified truths in `vault/truth/truths.jsonl`

### Output

The script generates:

1. **Console Output**: Detailed progress and results from each engine
2. **REPO_STUDY_REPORT.json**: Comprehensive JSON report with:
   - Study metadata (timestamp, engines used)
   - Parser insights (documents, chunks, bytes)
   - Blueprint insights (objectives, tasks, plans)
   - Truth insights (certified facts, sources)
   - Key findings and conclusions

3. **Vault Data**:
   - `vault/parser/chunks/` - Content chunks (SHA256-addressed text files)
   - `vault/parser/meta/` - Chunk metadata (tags, lineage, sources)
   - `vault/parser/ledger.jsonl` - Event log of all parser operations
   - `vault/truth/truths.jsonl` - Certified repository facts

## Example Output

```
╔═══════════════════════════════════════════════════════════════════════════╗
║         SR-AIbridge Repository Study Using Three Core Engines             ║
║   Parser Engine  →  Ingest & chunk repository documentation              ║
║   Blueprint Engine → Create structured analysis plans                     ║
║   Truth Engine   →  Certify & validate repository facts                  ║
╚═══════════════════════════════════════════════════════════════════════════╝

STEP 1: Parser Engine - Repository Documentation Ingestion
═══════════════════════════════════════════════════════════
📄 Ingesting: README.md
   ✓ Seen: 37 chunks
   ✓ Filed: 37 new chunks
   ✓ Total bytes: 106,565

STEP 2: Blueprint Engine - Repository Analysis Planning
═══════════════════════════════════════════════════════════
📋 Creating analysis blueprint...
✓ Blueprint generated:
   📌 Objectives: 5
   📋 Tasks: 5
   📦 Artifacts: 2

STEP 3: Truth Engine - Repository Fact Certification
═══════════════════════════════════════════════════════════
📊 Certifying repository facts...
✓ Truth binding complete:
   Certified truths: 7
   Total source references: 7

🎉 Repository study complete! Check REPO_STUDY_REPORT.json for details.
```

## Understanding the Integration

### How the Three Engines Work Together

```
┌─────────────────┐
│  Parser Engine  │  Ingests documentation → Creates searchable knowledge base
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Blueprint Engine │  Analyzes requirements → Generates structured plans
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Truth Engine   │  Validates facts → Certifies repository state
└─────────────────┘
```

### Data Flow

1. **Parser Engine** chunks and indexes content
2. **Blueprint Engine** uses indexed knowledge to create analysis plans
3. **Truth Engine** validates facts extracted during analysis
4. All three engines maintain provenance and lineage
5. Results feed back into the knowledge base for future analysis

### Use Cases

This integrated approach enables:

- **Autonomous Documentation Analysis** - Self-documenting systems that understand their own architecture
- **Fact-Based Deployment Validation** - Verify system state against known truths
- **Knowledge Graph Construction** - Build linked knowledge from unstructured content
- **Intelligent Planning** - Generate execution plans from natural language goals
- **Provenance Tracking** - Maintain complete audit trail of facts and decisions

## Advanced Usage

### Custom Analysis

Modify the script to analyze different aspects:

```python
# Add custom documents to ingest
docs_to_ingest = [
    ("MY_CUSTOM_DOC.md", "Custom documentation"),
    ("API_SPEC.yaml", "API specification"),
]

# Create custom analysis brief
custom_brief = """
    Analyze the authentication and authorization patterns
    used across all API endpoints in the system.
"""

# Define custom facts to certify
custom_facts = [
    {
        "fact": "All API endpoints require JWT authentication",
        "sources": [{"sha": "api_doc", "ts": "2024-11-04", "source": "API_SPEC.yaml"}]
    }
]
```

### Querying Results

```python
from bridge_core.engines.parser.service import ParserEngine

parser = ParserEngine()

# Search for specific content
results = parser.search("authentication", limit=10)

# List chunks by tag
tagged = parser.list(tag="security", limit=20)

# Get specific chunk with lineage
chunk_info = parser.manifest("chunk_sha256_here")
```

### Analyzing Blueprints

```python
from bridge_core.engines.blueprint.blueprint_engine import BlueprintEngine

blueprint = BlueprintEngine()

# Generate analysis plan
plan = blueprint.draft("Audit security practices across the codebase")

# Inspect task dependencies
for task in plan['tasks']:
    print(f"{task['key']}: {task['title']}")
    print(f"  Depends on: {task['depends_on']}")
```

### Validating Truths

```python
from bridge_core.engines.truth.binder import list_truths

# Get all certified truths
truths = list_truths(limit=100)

for truth in truths['truths']:
    print(f"Truth: {truth['statement']}")
    print(f"  ID: {truth['truth_id']}")
    print(f"  Sources: {len(truth['sources'])}")
```

## Architecture Benefits

### Why These Three Engines?

1. **Parser Engine**: Provides the **knowledge layer** - ingests and indexes information
2. **Blueprint Engine**: Provides the **planning layer** - transforms goals into actionable tasks
3. **Truth Engine**: Provides the **validation layer** - ensures correctness and provenance

Together, they enable:
- **Self-awareness** - System can analyze its own structure
- **Self-planning** - System can plan actions from natural language
- **Self-validation** - System can verify its own state
- **Autonomous operation** - Minimal human intervention required

### Event-Driven Integration

The engines communicate via the **Genesis Linkage** event bus:

- **Parser**: Publishes `parser.content`, `parser.lineage`
- **Blueprint**: Publishes `blueprint.events`
- **Truth**: Publishes `deploy.facts`, subscribes to `deploy.signals`

This enables:
- Asynchronous processing
- Loose coupling
- Event replay and audit
- Distributed operation

## Next Steps

1. **Extend the Study Script**: Add analysis of code files, not just documentation
2. **Create Custom Engines**: Build domain-specific engines that use these three as foundation
3. **Automate CI/CD Validation**: Use Truth Engine to validate deployments
4. **Build Knowledge Graphs**: Link parser chunks via truth relationships
5. **Implement Auto-Documentation**: Use Blueprint Engine to plan documentation updates

## References

- [Blueprint Engine Guide](BLUEPRINT_ENGINE_GUIDE.md)
- [Engine Catalog](ENGINE_CATALOG.md) - Complete documentation of all 20 engines
- [System Blueprint](SYSTEM_BLUEPRINT.md) - Architecture overview
- [Documentation Index](DOCUMENTATION_INDEX.md) - Master documentation map

## Support

For questions or issues:
- Check the [ENGINE_CATALOG.md](ENGINE_CATALOG.md) for detailed engine documentation
- Review [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) for guides and references
- Open an issue on GitHub with the `engines` label
