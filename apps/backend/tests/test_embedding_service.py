"""
Test script for EmbeddingService
Run this to verify the embedding service is working correctly
"""

import sys
import logging
from apps.backend.app.agents.Resume_Intelligence_agent.services.embedding_service import (
    EmbeddingService,
    get_embedding_service,
    reset_embedding_service
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_single_embedding():
    """Test single text embedding"""
    print("\n" + "="*60)
    print("TEST 1: Single Text Embedding")
    print("="*60)
    
    try:
        service = EmbeddingService(cache_enabled=False)
        text = "Senior Python Developer with 5 years experience"
        
        print(f"Embedding text: '{text}'")
        embedding = service.embed_text(text)
        
        print(f"✓ Embedding generated successfully")
        print(f"  Dimension: {len(embedding)}")
        print(f"  First 5 values: {embedding[:5]}")
        print(f"  Sum: {sum(embedding):.4f}")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def test_batch_embedding():
    """Test batch embedding"""
    print("\n" + "="*60)
    print("TEST 2: Batch Embedding")
    print("="*60)
    
    try:
        service = EmbeddingService(cache_enabled=False)
        texts = ["Python", "JavaScript", "SQL", "React", "Django"]
        
        print(f"Embedding {len(texts)} texts: {texts}")
        embeddings = service.embed_batch(texts)
        
        print(f"✓ Batch embedding completed")
        print(f"  Number of embeddings: {len(embeddings)}")
        print(f"  Dimension of each: {len(embeddings[0])}")
        print(f"  All dimensions valid: {all(len(e) == 768 for e in embeddings)}")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def test_caching():
    """Test embedding caching"""
    print("\n" + "="*60)
    print("TEST 3: Embedding Cache")
    print("="*60)
    
    try:
        service = EmbeddingService(cache_enabled=True)
        text = "Cache Test Text"
        
        print(f"First embedding of: '{text}'")
        e1 = service.embed_text(text)
        
        print(f"Second embedding of same text (should be from cache)")
        e2 = service.embed_text(text)
        
        if e1 == e2:
            print(f"✓ Cache working correctly - embeddings are identical")
        else:
            print(f"✗ Embeddings differ unexpectedly")
            return False
        
        stats = service.get_cache_stats()
        print(f"  Cache stats: {stats}")
        
        service.save_cache()
        print(f"✓ Cache saved to disk")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def test_batch_with_metadata():
    """Test batch embedding with metadata"""
    print("\n" + "="*60)
    print("TEST 4: Batch Embedding with Metadata")
    print("="*60)
    
    try:
        service = EmbeddingService(cache_enabled=False)
        
        data = [
            {"text": "Python", "metadata": {"type": "language", "level": "expert"}},
            {"text": "JavaScript", "metadata": {"type": "language", "level": "intermediate"}},
            {"text": "React", "metadata": {"type": "framework", "level": "advanced"}},
        ]
        
        print(f"Embedding {len(data)} items with metadata")
        result = service.embed_batch_with_metadata(data)
        
        print(f"✓ Batch with metadata completed")
        print(f"  Results: {len(result)} items")
        
        for i, item in enumerate(result):
            print(f"  Item {i+1}:")
            print(f"    Text: {item['text']}")
            print(f"    Metadata: {item['metadata']}")
            print(f"    Embedding dim: {len(item['embedding'])}")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def test_singleton():
    """Test singleton pattern"""
    print("\n" + "="*60)
    print("TEST 5: Singleton Pattern")
    print("="*60)
    
    try:
        reset_embedding_service()
        
        service1 = get_embedding_service()
        service2 = get_embedding_service()
        
        if service1 is service2:
            print(f"✓ Singleton pattern working - same instance returned")
        else:
            print(f"✗ Different instances returned")
            return False
        
        # Test embedding
        embedding = service1.embed_text("Test")
        print(f"✓ Embedding from singleton: dimension={len(embedding)}")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def test_error_handling():
    """Test error handling"""
    print("\n" + "="*60)
    print("TEST 6: Error Handling")
    print("="*60)
    
    try:
        service = EmbeddingService(cache_enabled=False)
        
        # Test empty text
        print("Testing empty text...")
        emb = service.embed_text("")
        if len(emb) == 768 and emb[0] == 0.0:
            print(f"✓ Empty text handled - returned zero vector")
        else:
            print(f"✗ Unexpected behavior for empty text")
            return False
        
        # Test None
        print("Testing None input...")
        emb = service.embed_text(None)
        if len(emb) == 768 and emb[0] == 0.0:
            print(f"✓ None input handled - returned zero vector")
        else:
            print(f"✗ Unexpected behavior for None input")
            return False
        
        # Test invalid type
        print("Testing invalid type...")
        emb = service.embed_text(123)
        if len(emb) == 768 and emb[0] == 0.0:
            print(f"✓ Invalid type handled - returned zero vector")
        else:
            print(f"✗ Unexpected behavior for invalid type")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def test_cache_stats():
    """Test cache statistics"""
    print("\n" + "="*60)
    print("TEST 7: Cache Statistics")
    print("="*60)
    
    try:
        service = EmbeddingService(cache_enabled=True)
        
        # Embed some texts
        texts = ["Python", "JavaScript", "Java", "Go", "Rust"]
        service.embed_batch(texts)
        
        stats = service.get_cache_stats()
        print(f"Cache Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print(f"✓ Cache stats retrieved successfully")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("EMBEDDING SERVICE TEST SUITE")
    print("="*60)
    
    tests = [
        ("Single Embedding", test_single_embedding),
        ("Batch Embedding", test_batch_embedding),
        ("Caching", test_caching),
        ("Batch with Metadata", test_batch_with_metadata),
        ("Singleton Pattern", test_singleton),
        ("Error Handling", test_error_handling),
        ("Cache Statistics", test_cache_stats),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"Test '{name}' crashed: {e}", exc_info=True)
            results.append((name, False))
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} | {name}")
    
    print("="*60)
    print(f"Total: {passed}/{total} tests passed ({100*passed/total:.1f}%)")
    print("="*60)
    
    return passed == total


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Test suite failed: {e}", exc_info=True)
        sys.exit(1)
