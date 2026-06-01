"""
extract text from resumes in various formats (PDF, DOCX) and ingest the extracted data into a vector database for semantic search and retrieval. The pipeline will also include error handling to manage cases where text extraction fails, ensuring that the ingestion process continues smoothly for valid files.
"""

from CustomException import CustomException
import logging
from pathlib import Path
from apps.backend.app.agents.Resume_Intelligence_agent.services.ingestion_services.extractor.orchestrator import ResumeOrchestrator, ExtractionMode
logger = logging.getLogger(__name__)

def text_extraction(mode, workers, file_path):
    """
    Extract text from resumes in various formats (PDF, DOCX) and update the StateGraph with the extracted text.
    Args:   
        mode (str): The extraction mode to use (fast, hybrid, llm).
        workers (int): The number of worker threads to use for parallel processing.
        file_path (str or list): The path to the resume file(s) to extract text from.
    Returns:
        dict: A dictionary mapping file paths to their extracted text and metadata.
    Raises:
        CustomException: If text extraction fails for any reason.
    """
    mode = ExtractionMode(mode)
    orch = ResumeOrchestrator(mode=mode, max_workers=workers)
    resume_text: dict[str, str] = {}
    try:
        # Handle both single path and list of paths
        if isinstance(file_path, list):
            paths = file_path
        else:
            paths = list(Path(file_path).glob("*.*"))
        print(f"Found {len(paths)} files for text extraction.")
        for file_path_item in paths:
            file_path_obj = Path(file_path_item)
            if file_path_obj.suffix.lower() == ".pdf":
                logger.info(f"Extracting text from PDF: {file_path_obj}")
                text = orch.pdf_to_text(file_path_obj)
                text = orch.clean_text(text)
            elif file_path_obj.suffix.lower() == ".docx":
                logger.info(f"Extracting text from DOCX: {file_path_obj}")
                text = orch.docx_to_text(file_path_obj)
                text = orch.clean_text(text)
            else:
                logging.warning(f"Unsupported file format: {file_path_obj}, skipping.")
                continue
            if text:
                resume_text[str(file_path_obj)] = {"text": text, "metadata": {"source": str(file_path_obj)}}
            else:
                logging.warning(f"Failed to extract text from {file_path_obj}, skipping.")
        
        return resume_text
    except Exception as e:
        logger.error(f"Error during text extraction: {e}")
        raise CustomException(f"Text extraction failed: {e}")

