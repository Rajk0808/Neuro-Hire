"""
Resume Extraction Orchestrator
================================
Combines all three extraction layers with a configurable fallback strategy:

  Mode 1 — FAST   : regex + spaCy only         (~2ms/resume)
  Mode 2 — HYBRID : regex + spaCy + LLM top-up (~1-2s/resume, best accuracy)
  Mode 3 — LLM    : full LLM extraction         (~1-2s/resume, max quality)

Usage:
    from orchestrator import ResumeOrchestrator, ExtractionMode

    orch = ResumeOrchestrator(mode=ExtractionMode.HYBRID)

    # Single resume
    result = orch.extract(text)
    print(result.to_json())

    # Thousands of resumes
    results = orch.batch_extract(texts)
"""

from __future__ import annotations

import logging
from dataclasses import asdict
from enum import Enum
from typing import Optional

from pipeline import ResumePipeline, ResumeData
from llm_extractor import extract_with_llm, batch_extract_with_llm

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# 1. EXTRACTION MODES
# ─────────────────────────────────────────────

class ExtractionMode(Enum):
    FAST   = "fast"      # regex + spaCy only
    HYBRID = "hybrid"    # regex + spaCy + LLM gap-filling
    LLM    = "llm"       # full LLM extraction


# ─────────────────────────────────────────────
# 2. FIELD PRIORITY RULES
# ─────────────────────────────────────────────

# Fields where LLM performs significantly better
_LLM_PREFERRED = {
    "skills",
    "experience",
    "education",
    "certifications",
    "projects",
    "languages",
    "extracurriculars",
    "publications",
    "summary",
    "job_title",
}

# Regex / deterministic fields that should never be overwritten
_REGEX_AUTHORITATIVE = {
    "email",
    "phones",
    "social_links",
}

# Fields where spaCy / heuristic extraction is usually reliable
_BASE_AUTHORITATIVE = {
    "name",
    "location",
}


# ─────────────────────────────────────────────
# 3. MERGE LOGIC
# ─────────────────────────────────────────────

def _is_empty(value) -> bool:
    """Return True if field is considered empty."""
    return value in (None, "", [], {}, ())


def _merge(base: ResumeData, llm_data: Optional[dict]) -> ResumeData:
    """
    Merge LLM output into a baseline ResumeData.

    Rules:
    ──────────────────────────────────────────
    1. Regex-authoritative fields are NEVER overwritten
    2. Existing non-empty deterministic fields are preserved
    3. LLM preferred fields may overwrite if richer/better
    4. Empty fields are always filled
    """

    if not llm_data:
        return base

    base_dict = asdict(base)

    for field_name, llm_val in llm_data.items():

        if field_name not in base_dict:
            continue

        if field_name in _REGEX_AUTHORITATIVE:
            continue

        current = base_dict[field_name]

        # Always fill empty values
        if _is_empty(current):
            base_dict[field_name] = llm_val
            continue

        # LLM-preferred semantic fields
        if field_name in _LLM_PREFERRED:

            # Prefer larger/richer lists
            if isinstance(current, list) and isinstance(llm_val, list):
                if len(llm_val) > len(current):
                    base_dict[field_name] = llm_val

            # Prefer longer summaries/descriptions
            elif isinstance(current, str) and isinstance(llm_val, str):
                if len(llm_val.strip()) > len(current.strip()):
                    base_dict[field_name] = llm_val

            # Replace if current malformed
            elif not current and llm_val:
                base_dict[field_name] = llm_val

    return ResumeData(**base_dict)


# ─────────────────────────────────────────────
# 4. ORCHESTRATOR
# ─────────────────────────────────────────────

class ResumeOrchestrator:
    """
    Main orchestration layer combining:
        • Regex extraction
        • spaCy NER
        • Heuristic section parsing
        • LLM extraction

    Supports:
        • Single resume extraction
        • Batch extraction
        • Hybrid fallback strategies
    """

    def __init__(
        self,
        mode: ExtractionMode = ExtractionMode.HYBRID,
        max_workers: int = 8,
        llm_batch_size: int = 5,
        rpm_limit: int = 50,
    ):
        self.mode = mode
        self.max_workers = max_workers
        self.llm_batch_size = llm_batch_size
        self.rpm_limit = rpm_limit

        # Fast extraction pipeline
        self._pipeline = ResumePipeline(
            max_workers=max_workers
        )

        logger.info(
            "ResumeOrchestrator initialized | mode=%s",
            self.mode.value,
        )

    # ─────────────────────────────────────────
    # SINGLE EXTRACTION
    # ─────────────────────────────────────────

    def extract(self, text: str) -> ResumeData:
        """
        Extract structured data from a single resume.
        """

        # ── FAST MODE ────────────────────────
        if self.mode == ExtractionMode.FAST:
            return self._pipeline.extract(text)

        # ── LLM MODE ─────────────────────────
        if self.mode == ExtractionMode.LLM:

            try:
                llm_data = extract_with_llm(text)

                if llm_data:

                    # Run deterministic extraction for reliable fields
                    base = self._pipeline.extract(text)

                    merged = {
                        **llm_data,
                        "email": base.email,
                        "phones": base.phones,
                        "social_links": base.social_links,
                    }

                    return _merge(
                        ResumeData(),
                        merged,
                    )

            except Exception as exc:
                logger.exception(
                    "LLM extraction failed: %s",
                    exc,
                )

            logger.warning(
                "Falling back to FAST extraction mode."
            )

            return self._pipeline.extract(text)

        # ── HYBRID MODE ──────────────────────
        base = self._pipeline.extract(text)

        try:
            llm_data = extract_with_llm(text)
            return _merge(base, llm_data)

        except Exception as exc:
            logger.exception(
                "Hybrid LLM enrichment failed: %s",
                exc,
            )

            return base

    # ─────────────────────────────────────────
    # BATCH EXTRACTION
    # ─────────────────────────────────────────

    def batch_extract(
        self,
        texts: list[str],
    ) -> list[ResumeData]:
        """
        Extract data from multiple resumes efficiently.

        Workflow:
            1. Parallel fast extraction
            2. Batched LLM enrichment
            3. Smart merge strategy
        """

        if not texts:
            return []

        # ── FAST MODE ────────────────────────
        if self.mode == ExtractionMode.FAST:
            return self._pipeline.batch_extract(texts)

        # Always run deterministic pipeline first
        bases = self._pipeline.batch_extract(texts)

        # ── BATCH LLM EXTRACTION ─────────────
        try:
            llm_results = batch_extract_with_llm(
                texts=texts,
                batch_size=self.llm_batch_size,
                rpm_limit=self.rpm_limit,
            )

        except Exception as exc:
            logger.exception(
                "Batch LLM extraction failed: %s",
                exc,
            )

            return bases

        merged_results: list[ResumeData] = []

        # ─────────────────────────────────────
        # FULL LLM MODE
        # ─────────────────────────────────────
        if self.mode == ExtractionMode.LLM:

            for base, llm_data in zip(bases, llm_results):

                if llm_data:

                    combined = {
                        **llm_data,
                        "email": base.email,
                        "phones": base.phones,
                        "social_links": base.social_links,
                    }

                    merged_results.append(
                        _merge(
                            ResumeData(),
                            combined,
                        )
                    )

                else:
                    merged_results.append(base)

            return merged_results

        # ─────────────────────────────────────
        # HYBRID MODE
        # ─────────────────────────────────────
        for base, llm_data in zip(bases, llm_results):
            merged_results.append(
                _merge(base, llm_data)
            )

        return merged_results