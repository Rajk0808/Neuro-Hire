"""
LLM Extraction Layer with Ollama (local models)
================================================
Uses Ollama for local LLM inference — no API keys needed!
Requires Ollama to be running: ollama serve
Download a model: ollama pull mistral (or llama2, neural-chat, etc.)

Falls back gracefully if Ollama is unavailable.
"""
import json
import time
import logging
from typing import Optional
from langchain_openrouter import ChatOpenRouter
import os
from dotenv import load_dotenv
load_dotenv()  

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """
You are a precise resume parser. Extract structured data from resume text.
Return ONLY valid JSON — no markdown fences, no explanation, no preamble.
Use null for missing fields, empty arrays [] for missing lists.

JSON schema (return exactly this shape):
{
  "name": string | null,
  "email": string | null,
  "phone": string | null,
  "location": string | null,
  "job_title": string | null,
  "skills": [{ "name": string, "category": string }],
  "experience": [{"title": string, "domain": string, "company": {"name": string, "sector": string | null, "size": string | null, "stage": string | null, "industry": string | null, "regulation": string | null}, "dates": string, "description": List[string]}],
  "education": [{"degree": string, "institution": string, "year": string, "gpa": string | null}],
  "certifications": [string],
  "projects": [{"name": string, "description": string, "technologies": [string]}],
  "languages": [string],
  "extracurriculars": [string],
  "summary": string | null,
  "publications": [string]
}
""".strip()

def _make_client():
    """Test connection to local Ollama server"""
    try:
        model = ChatOpenRouter(
                model="openai/gpt-oss-120b:free",
                temperature=0.8,
                api_key= os.getenv("OPENROUTER_API_KEY")
            )
        return model
    
    except Exception as e:
        logger.warning("Ollama not available at localhost:11434. Start with: ollama serve")
        logger.error("  Error: %s", str(e))
        return None


_client = None

def _get_client():
    global _client
    if _client is None:
        _client = _make_client()
    return _client


def extract_with_llm(resume_text: str, retries: int = 0) -> Optional[dict]:
    """
    Call local Ollama model to extract resume fields.
    Returns parsed dict or None on failure.
    """
    client = _get_client()
    if client is None:
        logger.debug("Ollama unavailable, falling back to fast extraction")
        return None
    
    for attempt in range(retries):
        try:
                        
            response = client.invoke(
                _SYSTEM_PROMPT + "\n\n" + resume_text
            )
            
            if response and response.content:
                raw = response.content
                raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                logger.info("LLM extraction successful (attempt %d)", attempt + 1)
                return json.loads(raw)
            else:
                logger.debug("Ollama returned empty response (attempt %d)", attempt + 1)
                if attempt < retries - 1:
                    time.sleep(1)

        except json.JSONDecodeError as e:
            logger.debug("LLM returned invalid JSON (attempt %d): %s", attempt + 1, str(e)[:100])
        except Exception as e:
            error_msg = str(e)[:150] if str(e) else type(e).__name__
            logger.warning("Ollama error (attempt %d): %s", attempt + 1, error_msg)
            if attempt < retries - 1:
                time.sleep(1)

    logger.debug("LLM extraction failed after %d retries, will use fast extraction", retries)
    return None


def batch_extract_with_llm(
    resume_texts: list[str],
    batch_size: int = 5,
    rpm_limit: int = 50,
) -> list[Optional[dict]]:
    """
    Extract from many resumes using local Ollama model.

    Args:
        resume_texts: list of raw resume text strings
        batch_size:   resumes per API call (reduces latency)
        rpm_limit:    (ignored for local model, no rate limit)

    Returns:
        list of dicts (same order as input), None for failures
    """
    client = _get_client()
    if client is None:
        return [None] * len(resume_texts)

    results: dict = {}
    successful_batches = 0

    for batch_start in range(0, len(resume_texts), batch_size):
        batch = resume_texts[batch_start: batch_start + batch_size]
        batch_prompt = "\n\n---\n\n".join(
            f"Resume {batch_start + i + 1}:\n{text}"
            for i, text in enumerate(batch)
        )
        full_prompt = (
            _SYSTEM_PROMPT + "\n\n" +
            f"Parse the following {len(batch)} resumes and return a JSON array.\n\n" +
            batch_prompt
        )

        t0 = time.monotonic()
        try:
            response = client.invoke(full_prompt)
            if response and response.content:
                raw = response.content
                raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                parsed = json.loads(raw)
                logger.info("Batch LLM extraction successful for resumes %d-%d", batch_start + 1, batch_start + len(batch))
                if isinstance(parsed, list):
                    for i, item in enumerate(parsed):
                        results[batch_start + i] = item
                else:
                    results[batch_start] = parsed
                successful_batches += 1
            else:
                logger.warning("Batch %d: empty response", batch_start)

        except json.JSONDecodeError as e:
            logger.warning("Batch %d: invalid JSON: %s", batch_start, str(e)[:100])
        except Exception as e:
            error_msg = str(e)[:150] if str(e) else type(e).__name__
            logger.warning("Batch %d failed: %s", batch_start, error_msg)

        elapsed = time.monotonic() - t0
        logger.debug("Batch %d processed in %.1fs", batch_start, elapsed)

    if successful_batches > 0:
        logger.info("Batch extraction: %d/%d batches succeeded", successful_batches, (len(resume_texts) + batch_size - 1) // batch_size)
    return [results.get(i) for i in range(len(resume_texts))]
