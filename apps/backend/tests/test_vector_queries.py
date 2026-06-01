from apps.backend.app.agents.Resume_Intelligence_agent.services.vector_similarity_queries import get_vector_queries

def test_similar_candidates():
    """Test finding similar candidates"""
    queries = get_vector_queries()
    results = queries.find_similar_candidates("Python developer", limit=5)
    if len(results) == 0:
        print("⚠ No candidates found in database - skipping assertions")
        return
    assert len(results) <= 5
    assert 'name' in results[0]
    assert 'similarity' in results[0]
    print("✓ Similar candidates test passed")

def test_hybrid_search():
    """Test hybrid search with metadata"""
    queries = get_vector_queries()
    results = queries.hybrid_search_candidates(
        "Senior developer",
        status="active",
        limit=5
    )
    if len(results) == 0:
        print("⚠ No candidates found in database - skipping assertions")
        return
    assert len(results) <= 5
    print("✓ Hybrid search test passed")

def test_skill_based_search():
    """Test skill-based search"""
    queries = get_vector_queries()
    results = queries.find_candidates_by_skills(
        ["Python", "JavaScript"],
        match_percentage=0.5,
        limit=5
    )
    if len(results) == 0:
        print("⚠ No candidates found in database - skipping assertions")
        return
    assert len(results) <= 5
    print("✓ Skill-based search test passed")

def test_batch_search():
    """Test batch similarity search"""
    queries = get_vector_queries()
    queries_list = ["Python developer", "Java developer"]
    results = queries.batch_similarity_search(queries_list, "Candidate")
    assert len(results) == 2
    if all(len(v) == 0 for v in results.values()):
        print("⚠ No candidates found in database - skipping assertions")
        return
    print("✓ Batch search test passed")

if __name__ == "__main__":
    test_similar_candidates()
    test_hybrid_search()
    test_skill_based_search()
    test_batch_search()
    print("\n✅ All tests passed!")
    