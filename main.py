from agents.Resume_Intelligence_agent.tools.skills_extractor import FreeSkillsExtractor
from agents.Resume_Intelligence_agent.schema.research_schema import SkillExtractorArgs
if __name__ == "__main__":  
    extractor = FreeSkillsExtractor()
    
    # Test the skill extractor
    result = extractor._run(
        SkillExtractorArgs(
            role="AI Engineer",
            domain="Technology",
            source="We are looking for a Software Engineer with 5+ years of experience in Python, Django, and REST APIs. Must have expertise in Docker and Kubernetes. Experience with PostgreSQL and Redis is required. Nice to have: AWS, CI/CD pipelines, and microservices architecture. We need a ninja who is passionate about code quality!"
        )
    )
    
    print("\n" + "="*60)
    print("🎯 SKILL EXTRACTION RESULTS")
    print("="*60)
    print(f"\n✅ MUST-HAVE SKILLS:")
    for skill in result['must_have_skills']:
        print(f"   • {skill}")
    
    print(f"\n💡 NICE-TO-HAVE SKILLS:")
    for skill in result['nice_to_have_skills']:
        print(f"   • {skill}")
    
    print(f"\n⚠️  ANTI-PATTERNS (Vague Terms):")
    for term in result['anti_pattern_skills']:
        print(f"   • {term}")
    
    print(f"\n📈 EMERGING SKILLS:")
    for skill in result['emerging_skills']:
        print(f"   • {skill}")
    
    print(f"\n🔍 SKILLS FROM GITHUB REPOS:")
    if result['github_skills']:
        for skill in result['github_skills']:
            print(f"   • {skill}")
    else:
        print("   (Could not fetch - API rate limit or no repos found)")
    
    print("\n" + "="*60)