from apps.backend.app.agents.Resume_Intelligence_agent.services.retrival_services.retrieval.neo4j_retrieval import neo4j_retrieval

def test_vector_query():
    """Test basic vector query"""
    retrieval = neo4j_retrieval()
    results = retrieval.built_vector_query("Python developer", limit=5)
    assert isinstance(results, list)
    print(f"✓ Vector query found {len(results)} results")

def test_job_matching():
    """Test job matching"""
    retrieval = neo4j_retrieval()
    results = retrieval.get_candidates_for_job_semantic("job_123", limit=10)
    assert isinstance(results, list)
    print(f"✓ Job matching found {len(results)} results")

def test_hybrid_search():
    """Test hybrid search"""
    retrieval = neo4j_retrieval()
    results = retrieval.search_candidates_hybrid(
        "Backend developer",
        status="active",
        limit=5
    )
    assert isinstance(results, list)
    print(f"✓ Hybrid search found {len(results)} results")

def test_skill_search():
    """Test skill-based search"""
    retrieval = neo4j_retrieval()
    results = retrieval.get_candidates_by_required_skills(
        ["Python"],
        match_percentage=0.5,
        limit=5
    )
    assert isinstance(results, list)
    print(f"✓ Skill search found {len(results)} results")

if __name__ == "__main__":
    test_vector_query()
    test_job_matching()
    test_hybrid_search()
    test_skill_search()
    print("\n✅ All retrieval tests passed!")
