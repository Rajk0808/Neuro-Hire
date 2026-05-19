"""Integration Example: DEI Language Auditor + Bias Guardian Agent"""
import asyncio
from agents.Resume_Intelligence_agent.tools.dei_language_auditor_tool import DEILanguage
from agents.Resume_Intelligence_agent.tools.Bias_Guardian_agent.bias_guardian import BiasGuardianAgent


def setup_dei_with_escalation():
    """
    Set up DEI Language Auditor with Bias Guardian escalation.
    
    Returns:
        Configured DEILanguage instance with escalation handler
    """
    # Initialize Bias Guardian agent
    bias_guardian = BiasGuardianAgent()
    
    # Create DEI auditor with escalation handler
    dei_auditor = DEILanguage(escalation_handler=bias_guardian.handle_escalation)
    
    return dei_auditor, bias_guardian


async def audit_job_description_with_escalation(
    job_description: str,
    threshold: float = 20.0
):
    """
    Audit a job description with automatic escalation if bias exceeds threshold.
    
    Args:
        job_description: Job description text to audit
        threshold: Bias score threshold for escalation (default: 20%)
        
    Returns:
        Complete audit report including escalation details if applicable
    """
    dei_auditor, bias_guardian = setup_dei_with_escalation()
    
    # Run the audit
    audit_result = await dei_auditor.evaluate_jd(job_description, threshold)
    
    print("\n" + "="*70)
    print("DEI LANGUAGE AUDIT REPORT")
    print("="*70)
    print(f"\n📊 Bias Score: {audit_result['bias_score']:.2f}%")
    print(f"⚙️  Threshold: {threshold}%")
    print(f"✅ Recommendation: {audit_result['recommendation']}")
    
    if audit_result['flagged_words']:
        print(f"\n⚠️  Flagged Terms ({len(audit_result['flagged_words'])}):")
        for word, suggestion in zip(audit_result['flagged_words'], audit_result['replacement_suggestions']):
            print(f"   • '{word}' → '{suggestion}'")
    
    # Handle escalation if triggered
    if audit_result['escalated']:
        escalation_report = audit_result['escalation_details']
        print("\n" + "="*70)
        print("🚨 ESCALATION REPORT - BIAS GUARDIAN ANALYSIS")
        print("="*70)
        print(f"\nEscalation ID: {escalation_report['escalation_id']}")
        print(f"Severity Level: {escalation_report['severity'].upper()}")
        print(f"Exceeded Threshold By: {escalation_report['score_exceeded_by']}%")
        print(f"Urgency: {escalation_report['urgency']}")
        
        print(f"\n📋 Detailed Analysis:")
        analysis = escalation_report['detailed_analysis']
        print(f"   Summary: {analysis['summary']}")
        print(f"   Patterns Detected: {', '.join(analysis['patterns_detected']) if analysis['patterns_detected'] else 'None'}")
        print(f"   Impact: {analysis['impact_assessment']}")
        
        print(f"\n✅ Actionable Recommendations:")
        for i, rec in enumerate(escalation_report['actionable_recommendations'], 1):
            print(f"   {i}. [{rec['priority']}] {rec['action']}")
        
        print("\n" + "="*70)
        print("ESCALATION SUMMARY")
        print("="*70)
        summary = bias_guardian.get_escalation_summary()
        print(f"Total Escalations: {summary['total_escalations']}")
        print(f"Average Bias Score: {summary['average_bias_score']:.2f}%")
        print(f"Highest Bias Score: {summary['highest_bias_score']:.2f}%")
    
    print("\n" + "="*70)
    return audit_result


if __name__ == "__main__":
    # Example job descriptions to test
    test_jds = [
        {
            "title": "Senior Software Engineer",
            "description": "We are looking for a ninja rockstar who is aggressive and dominant in the marketplace. We need a guru programmer with strong aggressive attitude. Salesman experience preferred. He must be understanding and supportive.",
            "threshold": 20.0
        },
        {
            "title": "Product Manager",
            "description": "We seek a collaborative and empathetic leader to join our diverse team. We value inclusive language and are committed to creating an equitable workplace for all candidates.",
            "threshold": 20.0
        },
        {
            "title": "Marketing Manager",
            "description": "Strong marketing professional needed. Aggressive tactics required. Must be a rockstar performer. Looking for salespeople with dominant personalities.",
            "threshold": 15.0
        }
    ]
    
    # Run audits
    async def run_audits():
        for test in test_jds:
            print(f"\n\n{'#'*70}")
            print(f"Testing: {test['title']}")
            print(f"{'#'*70}")
            await audit_job_description_with_escalation(
                test['description'],
                test['threshold']
            )
    
    asyncio.run(run_audits())
