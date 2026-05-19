"""
Demo: Competitor JD Analyzer
Shows pattern analysis, gap identification, and competitive opportunities
"""

from agents.Resume_Intelligence_agent.tools.competitor_analyzer import CompetitorJDAnalyzer
from agents.Resume_Intelligence_agent.schema.research_schema import CompetitorJDAnalysisArgs

def demo_competitor_analysis():
    """Demonstrate competitor JD analysis."""
    
    print("\n" + "="*70)
    print("🏢 COMPETITOR JD ANALYZER - DEMO")
    print("="*70)
    
    # Initialize analyzer
    analyzer = CompetitorJDAnalyzer()
    
    # Target companies and role
    companies = ["Google", "Meta", "Microsoft", "Amazon", "Apple"]
    role = "Senior Software Engineer"
    seniority = "senior"
    
    print(f"\n🎯 Analyzing competitors: {', '.join(companies)}")
    print(f"📝 Role: {role} ({seniority})")
    print("\n⏳ Fetching and analyzing JDs...")
    print("   (Using cache for 24h, web scraping as fallback)\n")
    
    # Run analysis
    args = CompetitorJDAnalysisArgs(companies=companies, role=role, seniority=seniority)
    result = analyzer._run(args)
    
    # Display Results
    print("\n" + "-"*70)
    print("📊 ANALYSIS SUMMARY")
    print("-"*70)
    print(f"✓ Companies Analyzed: {result['companies_analyzed']}")
    print(f"⏰ Timestamp: {result['timestamp']}")
    
    # Individual Company Insights
    print("\n" + "-"*70)
    print("🔍 INDIVIDUAL COMPANY INSIGHTS")
    print("-"*70)
    
    for company, analysis in result['individual_analyses'].items():
        print(f"\n{company}:")
        print(f"  • Sections: {', '.join(analysis['sections_found'][:3])}")
        print(f"  • JD Length: {analysis['text_length']} chars")
        print(f"  • Required Skills: {', '.join(analysis['required_skills'][:3])}")
        if analysis['compensation']['salary_range']:
            print(f"  • Salary: {analysis['compensation']['salary_range']}")
        else:
            print(f"  • Salary: ❌ NOT DISCLOSED")
        print(f"  • Differentiators: {', '.join(analysis['differentiators'][:2]) if analysis['differentiators'] else 'None'}")
    
    # Structural Patterns
    print("\n" + "-"*70)
    print("📐 STRUCTURAL PATTERNS ACROSS COMPETITORS")
    print("-"*70)
    
    patterns = result['structural_patterns']
    print(f"\n✅ Common Sections Found:")
    for section in patterns['common_sections']:
        print(f"   • {section.replace('_', ' ').title()}")
    
    print(f"\n🎯 Most Common Required Skills:")
    for i, skill in enumerate(patterns['most_common_skills'][:5], 1):
        print(f"   {i}. {skill}")
    
    print(f"\n📏 Average JD Length: {patterns['average_jd_length']} characters")
    
    print(f"\n💼 Compensation Trends:")
    comp = patterns['compensation_trends']
    print(f"   • Companies disclosing salary: {comp['companies_with_salary_info']}/{result['companies_analyzed']}")
    print(f"   • Companies offering equity: {comp['companies_with_equity']}/{result['companies_analyzed']}")
    print(f"   • Companies offering bonuses: {comp['companies_with_bonus']}/{result['companies_analyzed']}")
    print(f"   • Salary Transparency Rate: {comp['average_transparency']}%")
    
    print(f"\n🎨 Writing Style:")
    tone = patterns['tone_characteristics']
    print(f"   • Formal: {tone.get('is_formal', 0)} companies")
    print(f"   • Casual: {tone.get('is_casual', 0)} companies")
    print(f"   • Technical: {tone.get('is_technical', 0)} companies")
    
    # Identified Gaps
    print("\n" + "-"*70)
    print("🕳️  IDENTIFIED GAPS (Your Opportunity)")
    print("-"*70)
    
    gaps = result['identified_gaps']
    
    print(f"\n💰 Salary Transparency Gap:")
    salary_gap = gaps['salary_transparency_gap']
    if salary_gap['companies_without_salary']:
        print(f"   Companies NOT disclosing: {', '.join(salary_gap['companies_without_salary'])}")
        print(f"   ➜ Opportunity: Be first to publish salary ranges!")
    
    print(f"\n📋 Missing Differentiators ({gaps['missing_differentiators']['opportunity_count']} opportunities):")
    for diff in list(gaps['missing_differentiators']['competitors_not_highlighting'])[:5]:
        print(f"   • {diff}")
    print(f"   ➜ Opportunity: Highlight unique benefits competitors ignore")
    
    # Competitive Opportunities
    print("\n" + "-"*70)
    print("🚀 COMPETITIVE OPPORTUNITIES")
    print("-"*70)
    
    opportunities = result['competitive_opportunities']
    for i, opp in enumerate(opportunities, 1):
        print(f"\n{i}. {opp['category'].upper()}")
        print(f"   Gap: {opp['gap']}")
        print(f"   Opportunity: {opp['opportunity']}")
        print(f"   Action: → {opp['action']}")
    
    # Generated Parser Code
    print("\n" + "-"*70)
    print("🔧 AUTO-GENERATED JD PARSER CODE")
    print("-"*70)
    print("\nGenerated Python parser for parsing future JDs:")
    print(result['generated_parser_code'][:500] + "...\n")
    
    print("="*70)
    print("✨ Analysis complete! Check .jd_cache/ for cached results (24h TTL)")
    print("="*70 + "\n")
    
    return result


if __name__ == "__main__":
    demo_competitor_analysis()
