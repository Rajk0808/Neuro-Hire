# Resume NLP Extraction Pipeline

Extracts 14 structured fields from raw resume text — built for processing
**thousands of resumes** with minimal latency and maximum accuracy.

## Architecture

```
Raw Resume Text
      │
      ▼
┌─────────────────────────────┐
│   Layer 1 · Regex           │  email, phone  (~0.1ms)
└──────────────┬──────────────┘
               │
      ▼
┌─────────────────────────────┐
│   Layer 2 · spaCy NER       │  name, location  (~1-5ms)
└──────────────┬──────────────┘
               │
      ▼
┌─────────────────────────────┐
│   Layer 2b · Section Parser │  section chunking + heuristic field parsing
└──────────────┬──────────────┘
               │
      ▼ (HYBRID / LLM mode only)
┌─────────────────────────────┐
│   Layer 3 · LLM (Claude)    │  semantic fields, fills gaps  (~1-2s)
└──────────────┬──────────────┘
               │
      ▼
┌─────────────────────────────┐
│   Merge & Output            │  ResumeData dataclass → JSON
└─────────────────────────────┘
```

## Extracted Fields

| Field | Layer |
|---|---|
| `name` | spaCy NER + heuristic fallback |
| `email` | Regex |
| `phone` | Regex |
| `location` | spaCy NER |
| `job_title` | spaCy NER + heuristic |
| `skills` | Section parser + LLM |
| `experience` | Section parser + LLM |
| `education` | Section parser + LLM |
| `certifications` | Section parser + LLM |
| `projects` | Section parser + LLM |
| `languages` | Section parser + LLM |
| `extracurriculars` | Section parser + LLM |
| `summary` | Section parser + LLM |
| `publications` | Section parser + LLM |

## Installation

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Usage

### Python API

```python
from orchestrator import ResumeOrchestrator, ExtractionMode

orch = ResumeOrchestrator(mode=ExtractionMode.HYBRID)

# Single resume
result = orch.extract(resume_text)
print(result.to_json())

# Batch (thousands of resumes)
results = orch.batch_extract(texts)   # threaded, returns list[ResumeData]
```

### CLI

```bash
# Demo run (no input needed)
python run.py

# Fast mode (regex + NER only, no API key required)
python run.py --mode fast --file resume.txt

# Hybrid mode (best for production)
ANTHROPIC_API_KEY=sk-... python run.py --mode hybrid --input resumes/

# Full LLM mode (maximum quality)
ANTHROPIC_API_KEY=sk-... python run.py --mode llm --file resume.txt --output result.json
```

## Extraction Modes

| Mode | Speed | Quality | API Key? |
|---|---|---|---|
| `fast` | ~2ms/resume | Good | No |
| `hybrid` | ~1-2s/resume | Best | Yes |
| `llm` | ~1-2s/resume | Best | Yes |

## Scaling to Thousands of Resumes

- **`batch_extract()`** runs the fast pipeline in a `ThreadPoolExecutor` (default 8 workers).
- LLM calls are batched (5 resumes per API call by default) to minimise round-trips.
- Rate limiting is built in (configurable `rpm_limit`, default 50 req/min).
- The spaCy model is loaded **once** at startup and shared across all threads (read-only, thread-safe).

For very large datasets (100k+), consider running multiple processes with `multiprocessing` and splitting the corpus.
