"""
Embedding Service for Vectorized Knowledge Graph
Wrapper around QwenMultimodalEmbeddingFunction with caching and batch processing
"""

import hashlib
import json
import logging
from typing import List, Dict, Optional, Union
import numpy as np
from custom_llm.EmbeddingHuggingFace import QwenMultimodalEmbeddingFunction, get_embeddings
from dotenv import load_dotenv
import os

load_dotenv()
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Embedding model configuration
# nvidia/llama-nemotron-embed-vl-1b-v2:free returns 384-dimensional embeddings
EMBEDDING_MODEL_DIMENSION = 384  # Qwen multimodal embedding dimension
BATCH_SIZE = 32  # Number of texts to embed in one batch
CACHE_ENABLED = True  # Enable/disable embedding cache
CACHE_PATH = os.path.join(os.path.dirname(__file__), "..", "embedding_cache.json")

# Zero vector fallback (used when embedding fails)
ZERO_VECTOR = [0.0] * EMBEDDING_MODEL_DIMENSION


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _to_list(embedding) -> Optional[List[float]]:
    """
    Convert embedding to list, handling numpy arrays and other types.
    
    Args:
        embedding: Embedding in any format
    
    Returns:
        List of floats or None if invalid
    """
    try:
        if embedding is None:
            return None
        
        # Convert numpy array to list
        if isinstance(embedding, np.ndarray):
            return embedding.tolist()
        
        # Already a list
        if isinstance(embedding, list):
            return embedding
        
        # Try to convert to list
        return list(embedding)
    except Exception as e:
        logger.warning(f"Failed to convert embedding to list: {e}")
        return None


# ============================================================================
# EMBEDDING CACHE CLASS
# ============================================================================

class EmbeddingCache:
    """
    Manages embedding cache to avoid redundant API calls.
    Stores embeddings in JSON file for persistence.
    """
    
    def __init__(self, cache_file: str = CACHE_PATH):
        """
        Initialize embedding cache.
        
        Args:
            cache_file: Path to cache file
        """
        self.cache_file = cache_file
        self.cache: Dict[str, List[float]] = self._load_cache()
        logger.info(f"EmbeddingCache initialized with {len(self.cache)} cached entries")
    
    def _load_cache(self) -> Dict[str, List[float]]:
        """
        Load cache from file.
        
        Returns:
            Dictionary of cached embeddings (hash -> embedding vector)
        """
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)
                    logger.info(f"Loaded {len(cache)} embeddings from cache file")
                    return cache
            else:
                logger.info("Cache file not found, starting with empty cache")
                return {}
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}, starting with empty cache")
            return {}
    
    def save_cache(self):
        """
        Persist cache to disk.
        Call this before application shutdown to save embeddings.
        """
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f)
            logger.info(f"Cache saved: {len(self.cache)} entries written to {self.cache_file}")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    def get(self, text: str) -> Optional[List[float]]:
        """
        Retrieve embedding from cache.
        
        Args:
            text: Original text
        
        Returns:
            Embedding vector if found, None otherwise
        """
        key = self._hash_text(text)
        return self.cache.get(key)
    
    def set(self, text: str, embedding: List[float]):
        """
        Store embedding in cache.
        
        Args:
            text: Original text
            embedding: Embedding vector
        """
        key = self._hash_text(text)
        self.cache[key] = embedding
    
    @staticmethod
    def _hash_text(text: str) -> str:
        """
        Create consistent hash key from text.
        
        Args:
            text: Text to hash
        
        Returns:
            MD5 hash of text
        """
        return hashlib.md5(text.encode()).hexdigest()
    
    def clear(self):
        """
        Clear all cached embeddings.
        """
        old_size = len(self.cache)
        self.cache.clear()
        logger.info(f"Cache cleared: {old_size} entries removed")
    
    def get_stats(self) -> Dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache info
        """
        return {
            "total_cached": len(self.cache),
            "cache_file": self.cache_file,
            "file_exists": os.path.exists(self.cache_file),
            "cache_size_mb": os.path.getsize(self.cache_file) / 1024 / 1024 
                            if os.path.exists(self.cache_file) else 0
        }


# ============================================================================
# MAIN EMBEDDING SERVICE CLASS
# ============================================================================

class EmbeddingService:
    """
    Main service for generating and managing embeddings.
    
    Provides:
    - Single text embedding
    - Batch embedding with caching
    - Error handling with fallback to zero vectors
    - Cache persistence
    
    Usage:
        service = EmbeddingService()
        embedding = service.embed_text("Senior Python Developer")
        embeddings = service.embed_batch(["Python", "JavaScript", "SQL"])
    """
    
    def __init__(self, cache_enabled: bool = CACHE_ENABLED):
        """
        Initialize EmbeddingService.
        
        Args:
            cache_enabled: Whether to enable caching
        """
        try:
            self.embedding_function = QwenMultimodalEmbeddingFunction()
            self.cache = EmbeddingCache() if cache_enabled else None
            self.cache_enabled = cache_enabled
            self.embedding_dim = EMBEDDING_MODEL_DIMENSION
            logger.info(
                f"EmbeddingService initialized successfully "
                f"(cache_enabled={cache_enabled}, dimension={self.embedding_dim})"
            )
        except Exception as e:
            logger.error(f"Failed to initialize EmbeddingService: {e}")
            raise
    
    def embed_text(self, text: str, use_cache: bool = True) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            use_cache: Whether to check/use cache
        
        Returns:
            Embedding vector (list of floats)
        
        Raises:
            ValueError: If text is invalid or embedding fails
        
        Example:
            >>> service = EmbeddingService()
            >>> embedding = service.embed_text("Python developer")
            >>> len(embedding)
            384
        """
        # Validate input
        if not text or not isinstance(text, str):
            raise ValueError(f"Invalid text input: {repr(text)}")
        
        text = text.strip()
        if not text:
            raise ValueError("Empty text after stripping")
        
        # Check cache first
        if self.cache_enabled and use_cache:
            cached = self.cache.get(text)
            if cached is not None:
                logger.debug(f"Cache hit for text: {text[:50]}...")
                return cached
        
        try:
            # Generate embedding using the embedding function
            embedding = get_embeddings(text)
            embedding = _to_list(embedding)
            
            # Validate embedding
            if embedding is None or len(embedding) != self.embedding_dim:
                raise ValueError(
                    f"Invalid embedding returned (dim={len(embedding) if embedding else 0}), "
                    f"expected {self.embedding_dim}"
                )
            
            # Check for zero vector (which Neo4j will reject)
            if all(v == 0.0 for v in embedding):
                raise ValueError(
                    f"Embedding service returned zero vector (all values are 0.0). "
                    f"This likely indicates the embedding API failed. "
                    f"Check your API key and network connection."
                )
            
            # Store in cache
            if self.cache_enabled:
                self.cache.set(text, embedding)
            
            logger.debug(f"Generated embedding for text: {text[:50]}...")
            return embedding
        
        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            raise ValueError(f"Failed to embed text '{text[:50]}...': {e}")
    
    def embed_batch(self, texts: List[str], use_cache: bool = True) -> List[List[float]]:
        """
        Generate embeddings for multiple texts efficiently.
        Uses cache to avoid redundant API calls.
        
        Args:
            texts: List of texts to embed
            use_cache: Whether to use cache
        
        Returns:
            List of embedding vectors (same order as input)
        
        Example:
            >>> service = EmbeddingService()
            >>> texts = ["Python", "JavaScript", "Java"]
            >>> embeddings = service.embed_batch(texts)
            >>> len(embeddings)
            3
            >>> len(embeddings[0])
            384
        """
        if not texts:
            logger.warning("Empty text list provided to embed_batch")
            return []
        
        # Filter empty texts
        valid_texts = [t.strip() for t in texts if t and isinstance(t, str) and t.strip()]
        if not valid_texts:
            logger.warning("No valid texts in batch")
            return [ZERO_VECTOR.copy() for _ in texts]
        
        # Separate cached and uncached texts
        embeddings = {}  # Map from index to embedding
        uncached_texts = {}  # Map from index to text
        
        for i, text in enumerate(valid_texts):
            if self.cache_enabled and use_cache:
                cached = self.cache.get(text)
                if cached is not None:
                    embeddings[i] = cached
                else:
                    uncached_texts[i] = text
            else:
                uncached_texts[i] = text
        
        # Log cache performance
        cache_hits = len(embeddings)
        total_texts = len(valid_texts)
        if cache_hits > 0:
            logger.info(f"Cache hits: {cache_hits}/{total_texts} ({100*cache_hits/total_texts:.1f}%)")
        
        # If all texts are cached, return early
        if not uncached_texts:
            logger.info(f"All {total_texts} texts found in cache")
            result = [None] * total_texts
            for idx, emb in embeddings.items():
                result[idx] = emb
            return result
        
        # Generate embeddings for uncached texts
        try:
            texts_to_embed = [uncached_texts[idx] for idx in sorted(uncached_texts.keys())]
            logger.info(f"Generating embeddings for {len(texts_to_embed)} texts...")
            
            # Use the embedding function directly (it's callable)
            new_embeddings = self.embedding_function(texts_to_embed)
            
            # Convert to list format
            new_embeddings = [_to_list(emb) for emb in new_embeddings]
            
            # Validate new embeddings
            if len(new_embeddings) != len(texts_to_embed):
                logger.error(
                    f"Mismatch: requested {len(texts_to_embed)} embeddings, got {len(new_embeddings)}"
                )
                return [ZERO_VECTOR.copy() for _ in valid_texts]
            
            # Cache the new embeddings
            if self.cache_enabled:
                for text, embedding in zip(texts_to_embed, new_embeddings):
                    if embedding is not None and len(embedding) == self.embedding_dim:
                        self.cache.set(text, embedding)
            
            # Combine cached and new embeddings
            result = [None] * total_texts
            
            # Fill cached embeddings
            for idx, emb in embeddings.items():
                result[idx] = emb
            
            # Fill new embeddings
            sorted_uncached_indices = sorted(uncached_texts.keys())
            for i, idx in enumerate(sorted_uncached_indices):
                result[idx] = new_embeddings[i] if new_embeddings[i] else ZERO_VECTOR.copy()
            
            logger.info(
                f"Batch complete: {len(new_embeddings)} new + {cache_hits} cached = {total_texts} total"
            )
            return result
        
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            return [ZERO_VECTOR.copy() for _ in valid_texts]
    
    def embed_batch_with_metadata(
        self, 
        texts_with_metadata: List[Dict[str, Union[str, dict]]]
    ) -> List[Dict]:
        """
        Generate embeddings for texts with associated metadata.
        
        Args:
            texts_with_metadata: List of dicts with 'text' and 'metadata' keys
        
        Returns:
            List of dicts with 'embedding' and 'metadata' keys
        
        Example:
            >>> data = [
            ...     {"text": "Python", "metadata": {"type": "language"}},
            ...     {"text": "React", "metadata": {"type": "framework"}}
            ... ]
            >>> result = service.embed_batch_with_metadata(data)
            >>> result[0].keys()
            dict_keys(['embedding', 'metadata', 'text'])
        """
        texts = [item['text'] for item in texts_with_metadata]
        embeddings = self.embed_batch(texts)
        
        result = []
        for i, (item, embedding) in enumerate(zip(texts_with_metadata, embeddings)):
            result.append({
                'text': item['text'],
                'embedding': embedding,
                'metadata': item.get('metadata', {})
            })
        
        return result
    
    def clear_cache(self):
        """
        Clear all cached embeddings from memory.
        """
        if self.cache_enabled:
            self.cache.clear()
        else:
            logger.warning("Cache is not enabled")
    
    def save_cache(self):
        """
        Persist cache to disk.
        Should be called before application shutdown.
        """
        if self.cache_enabled:
            self.cache.save_cache()
        else:
            logger.warning("Cache is not enabled")
    
    def get_cache_stats(self) -> Dict:
        """
        Get statistics about cache usage.
        
        Returns:
            Dictionary with cache statistics
        """
        if not self.cache_enabled:
            return {"cache_enabled": False, "status": "Cache disabled"}
        
        return {
            "cache_enabled": True,
            **self.cache.get_stats()
        }
    
    def get_embedding_dimension(self) -> int:
        """
        Get the embedding vector dimension.
        
        Returns:
            Dimension (usually 768 for Qwen models)
        """
        return self.embedding_dim


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service(cache_enabled: bool = CACHE_ENABLED) -> EmbeddingService:
    """
    Get or create the global EmbeddingService instance (singleton pattern).
    
    This ensures only one instance is created and reused throughout the application.
    
    Args:
        cache_enabled: Whether to enable caching
    
    Returns:
        EmbeddingService instance
    
    Example:
        >>> service = get_embedding_service()
        >>> embedding = service.embed_text("Python")
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService(cache_enabled=cache_enabled)
    return _embedding_service


def reset_embedding_service():
    """
    Reset the global embedding service instance.
    Useful for testing or reinitializing.
    """
    global _embedding_service
    if _embedding_service:
        _embedding_service.save_cache()
    _embedding_service = None
    logger.info("Embedding service instance reset")

