"""Bias Guardian Agent - Escalation Handler for High Bias Scores"""
import asyncio
from typing import Dict, List, Any
from datetime import datetime


class BiasGuardianAgent:
    """
    Agent responsible for handling escalations from DEI Language Auditor.
    Generates detailed reports and recommendations for high-bias job descriptions.
    """
    
    def __init__(self):
        self.escalation_logs = []
        self.severity_levels = {
            "critical": (50, 100),    # Bias score 50-100
            "high": (30, 49.99),      # Bias score 30-49.99
            "medium": (15, 29.99),    # Bias score 15-29.99
            "low": (0, 14.99)         # Bias score 0-14.99
        }
    
    def determine_severity(self, bias_score: float) -> str:
        """Determine the severity level based on bias score."""
        for level, (min_score, max_score) in self.severity_levels.items():
            if min_score <= bias_score <= max_score:
                return level
        return "unknown"
    
    def handle_escalation(
        self,
        job_description: str,
        bias_score: float,
        threshold: float,
        flagged_words: List[str],
        replacement_suggestions: List[str]
    ) -> Dict[str, Any]:
        """
        Handle escalation from DEI Language Auditor.
        
        Args:
            job_description: The job description being audited
            bias_score: The calculated bias score
            threshold: The threshold that was exceeded
            flagged_words: List of flagged biased words
            replacement_suggestions: Corresponding replacement suggestions
            
        Returns:
            Escalation report with detailed analysis and recommendations
        """
        severity = self.determine_severity(bias_score)
        
        # Create escalation report
        report = {
            "escalation_id": f"ESC_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "severity": severity,
            "bias_score": bias_score,
            "threshold": threshold,
            "score_exceeded_by": round(bias_score - threshold, 2),
            "flagged_words_count": len(flagged_words),
            "detailed_analysis": self._generate_analysis(
                bias_score, severity, flagged_words, replacement_suggestions
            ),
            "actionable_recommendations": self._generate_recommendations(
                severity, flagged_words, replacement_suggestions
            ),
            "urgency": self._determine_urgency(bias_score, threshold)
        }
        
        # Log the escalation
        self.escalation_logs.append({
            "escalation_id": report["escalation_id"],
            "timestamp": report["timestamp"],
            "severity": severity,
            "bias_score": bias_score
        })
        
        return report
    
    def _generate_analysis(
        self,
        bias_score: float,
        severity: str,
        flagged_words: List[str],
        replacement_suggestions: List[str]
    ) -> Dict[str, Any]:
        """Generate detailed analysis of the biased language."""
        word_analysis = {}
        for word, suggestion in zip(flagged_words, replacement_suggestions):
            if word not in word_analysis:
                word_analysis[word] = {
                    "count": flagged_words.count(word),
                    "suggestion": suggestion
                }
        
        analysis = {
            "summary": self._get_severity_message(severity, bias_score),
            "word_frequency_analysis": word_analysis,
            "patterns_detected": self._detect_patterns(flagged_words),
            "impact_assessment": self._assess_impact(severity, bias_score)
        }
        
        return analysis
    
    def _detect_patterns(self, flagged_words: List[str]) -> List[str]:
        """Detect patterns in flagged words (e.g., gender bias, stereotypes, etc.)."""
        patterns = []
        
        gender_bias_words = {'he', 'she', 'him', 'her', 'his', 'hers', 'salesman', 'saleswoman', 
                            'policeman', 'policewoman', 'actor', 'actress', 'waiter', 'waitress'}
        stereotype_words = {'ninja', 'rockstar', 'guru', 'aggressive', 'dominant'}
        gender_specific = {'strong', 'nurturing', 'supportive', 'understanding'}
        
        if any(word in gender_bias_words for word in flagged_words):
            patterns.append("Gender-biased language detected")
        
        if any(word in stereotype_words for word in flagged_words):
            patterns.append("Stereotypical/cultural bias detected")
        
        if any(word in gender_specific for word in flagged_words):
            patterns.append("Gender-stereotyped characteristics detected")
        
        return patterns
    
    def _assess_impact(self, severity: str, bias_score: float) -> str:
        """Assess the potential impact of the biased language."""
        impact_messages = {
            "critical": f"CRITICAL: Bias score of {bias_score}% indicates severe bias that likely discourages diverse candidates from applying.",
            "high": f"HIGH: Bias score of {bias_score}% suggests significant biased language that may negatively impact candidate diversity.",
            "medium": f"MEDIUM: Bias score of {bias_score}% indicates moderate bias with recommendations for improvement.",
            "low": f"LOW: Bias score of {bias_score}% is acceptable with minor language refinements suggested."
        }
        return impact_messages.get(severity, "Unknown impact level")
    
    def _generate_recommendations(
        self,
        severity: str,
        flagged_words: List[str],
        replacement_suggestions: List[str]
    ) -> List[Dict[str, str]]:
        """Generate actionable recommendations for remediation."""
        recommendations = []
        
        # Priority-based recommendations
        priority_map = {
            "critical": "URGENT",
            "high": "HIGH",
            "medium": "MEDIUM",
            "low": "LOW"
        }
        
        # General recommendations by severity
        severity_actions = {
            "critical": [
                "Conduct immediate review of job description",
                "Involve HR and DEI team for comprehensive revision",
                "Consider legal review for compliance",
                "Schedule rewrite with diverse team members"
            ],
            "high": [
                "Schedule review within 48 hours",
                "Identify and replace all flagged terms",
                "Test revised JD with diverse focus group"
            ],
            "medium": [
                "Review flagged terms and replace as needed",
                "Consider adding inclusive language statements"
            ],
            "low": [
                "Minor refinements suggested",
                "Continue monitoring for consistency"
            ]
        }
        
        for action in severity_actions.get(severity, []):
            recommendations.append({
                "priority": priority_map[severity],
                "action": action
            })
        
        # Add word-specific recommendations
        for word, suggestion in zip(flagged_words, replacement_suggestions):
            if word not in [w for d in recommendations for w in d.values()]:
                recommendations.append({
                    "priority": priority_map[severity],
                    "action": f"Replace '{word}' with '{suggestion}'"
                })
        
        return recommendations
    
    def _determine_urgency(self, bias_score: float, threshold: float) -> str:
        """Determine urgency level based on how much threshold was exceeded."""
        difference = bias_score - threshold
        
        if difference > 30:
            return "CRITICAL - Immediate action required"
        elif difference > 15:
            return "HIGH - Address within 24 hours"
        elif difference > 5:
            return "MEDIUM - Address within 3 days"
        else:
            return "LOW - Address within 1 week"
    
    def _get_severity_message(self, severity: str, bias_score: float) -> str:
        """Get a human-readable message for severity level."""
        messages = {
            "critical": f"Critical bias detected: {bias_score}% - Severe language issues requiring immediate intervention",
            "high": f"High bias detected: {bias_score}% - Significant biased language present",
            "medium": f"Medium bias detected: {bias_score}% - Moderate biased language detected",
            "low": f"Low bias detected: {bias_score}% - Minor biased language suggestions"
        }
        return messages.get(severity, f"Bias score: {bias_score}%")
    
    async def handle_escalation_async(
        self,
        job_description: str,
        bias_score: float,
        threshold: float,
        flagged_words: List[str],
        replacement_suggestions: List[str]
    ) -> Dict[str, Any]:
        """Async version of escalation handler."""
        return await asyncio.to_thread(
            self.handle_escalation,
            job_description,
            bias_score,
            threshold,
            flagged_words,
            replacement_suggestions
        )
    
    def get_escalation_history(self) -> List[Dict[str, Any]]:
        """Retrieve all escalation logs."""
        return self.escalation_logs
    
    def get_escalation_summary(self) -> Dict[str, Any]:
        """Get a summary of escalations."""
        if not self.escalation_logs:
            return {"total_escalations": 0, "by_severity": {}}
        
        summary = {
            "total_escalations": len(self.escalation_logs),
            "by_severity": {},
            "highest_bias_score": max(log["bias_score"] for log in self.escalation_logs),
            "average_bias_score": sum(log["bias_score"] for log in self.escalation_logs) / len(self.escalation_logs)
        }
        
        for log in self.escalation_logs:
            severity = log["severity"]
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
        
        return summary
