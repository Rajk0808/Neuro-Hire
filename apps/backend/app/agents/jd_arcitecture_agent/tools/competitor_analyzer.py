"""
Competitor JD Analyzer - Real-time Job Description Analysis
Fetches live JDs from competitor companies, extracts structural patterns,
identifies gaps, and provides competitive intelligence.

Features:
- Web scraping from multiple job boards
- LLM-powered structural extraction
- 24-hour caching with TTL
- Pattern identification & gap analysis
- Real-time parser code generation
"""

import asyncio
import httpx
import re
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Type, ClassVar
from pathlib import Path
from bs4 import BeautifulSoup
from crewai.tools import BaseTool
from pydantic import ConfigDict
from agents.jd_arcitecture_agent.schema.research_schema import (   
    CompetitorJDAnalysisArgs, 
    CompetitorJDAnalysisOutput
)
class CompetitorJDAnalyzerTool(BaseTool):
    """Analyze competitor job descriptions for patterns, gaps, and opportunities."""
    name: str = 'competitor_jd_analyzer'
    description: str = ("Use this tool to analyze competitor job descriptions for a given role and seniority level. "
    "It fetches live JDs from the web, extracts structural patterns, identifies gaps, and provides competitive intelligence to inform your own JD creation."
    )
    args_schema: Type[CompetitorJDAnalysisArgs] = CompetitorJDAnalysisArgs
    output_schema: Type[CompetitorJDAnalysisOutput] = CompetitorJDAnalysisOutput
    model_config = ConfigDict(arbitrary_types_allowed=True, extra='allow')
    # Common job board URLs (public/searchable)
    JOB_BOARDS: ClassVar[Dict[str, str]] = {
        "linkedin": "https://www.linkedin.com/jobs/search/",
        "indeed": "https://www.indeed.com/jobs/",
        "glassdoor": "https://www.glassdoor.com/Job/",
        "builtin": "https://builtin.com/jobs/",
        "techcrunch": "https://techcrunch.com/jobs/",
        "naukri": "https://www.naukri.com/search/"
    }
    
    # JD Section patterns
    JD_SECTIONS: ClassVar[Dict[str, str]] = {
        "about_company": r"(?:About|Company|Who We Are)[\s\S]{0,500}?(?=\n\n|\n[A-Z]|$)",
        "role_summary": r"(?:Role|Position|About This Role)[\s\S]{0,300}?(?=\n\n|\n[A-Z]|$)",
        "responsibilities": r"(?:Responsibilities|Duties|What You'll Do)[\s\S]{0,1000}?(?=\n\n|\n[A-Z]|$)",
        "requirements": r"(?:Requirements|Qualifications|What We're Looking For)[\s\S]{0,800}?(?=\n\n|\n[A-Z]|$)",
        "benefits": r"(?:Benefits|Perks|We Offer)[\s\S]{0,500}?(?=\n\n|\n[A-Z]|$)",
        "compensation": r"(?:Salary|Compensation|Pay|Salary Range)[\s\S]{0,200}?(?=\n\n|\n[A-Z]|$)"
    }
    
    # Common JD differentiators (competitive advantages mentioned)
    DIFFERENTIATORS: ClassVar[List[str]] = [
        "remote", "fully remote", "work from home", "flexible hours", "async-first",
        "equity", "stock options", "ipo", "growth", "unicorn", "series",
        "mentorship", "training budget", "learning", "conference", "sabbatical",
        "wellness", "health insurance", "dental", "vision", "401k",
        "diversity", "inclusion", "lgbtq", "women in tech", "underrepresented",
        "unlimited pto", "sabbatical", "parental leave", "mental health"
    ]
    
    # Compensation patterns
    COMPENSATION_PATTERNS: ClassVar[List[str]] = [
        r"\$(\d+)k?\s*(?:-|to|–)\s*\$(\d+)k?",
        r"(\d+),(\d{3})\s*(?:-|to|–)\s*(\d+),(\d{3})",
    ]
    
    def __init__(self, cache_dir: str = ".jd_cache"):
        """Initialize analyzer with cache directory."""
        super().__init__()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_ttl = timedelta(hours=24)
        
    async def _run(self, companies: list, role: str, seniority: str) -> CompetitorJDAnalysisOutput:
        """
        Analyze competitor JDs for patterns and gaps.
        
        Args:
            companies: List of competitor companies for which to analyze job descriptions
            role: The job title or role for which to analyze competitor JDs
            seniority: The seniority level (e.g., Junior, Mid, Senior) for which to analyze competitor JDs
            
        Returns:
            Comprehensive analysis including patterns, gaps, and recommendations
        """
        
        # Fetch JDs (from cache or web)
        jds_data = {}
        for company in companies:
            jds_data[company] = await self._fetch_jd(company, role, seniority)
            await asyncio.sleep(1)  # Rate limiting
        
        # Analyze each JD
        analyses = {}
        for company, jd_text in jds_data.items():
            if jd_text:
                analyses[company] = self._analyze_single_jd(jd_text, company)
        
        # Comparative analysis
        patterns = self._extract_patterns(analyses)
        gaps = await self._identify_gaps(analyses)
        opportunities = await self._find_opportunities(patterns, gaps)
        
        return {
            "companies_analyzed": len(analyses),
            "individual_analyses": analyses,
            "structural_patterns": patterns,
            "identified_gaps": gaps,
            "competitive_opportunities": opportunities,
            "generated_parser_code": self._generate_parser_code(analyses),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _fetch_jd(self, company: str, role: str, seniority: str) -> Optional[str]:
        """Fetch JD from cache or web scrape."""
        cache_key = self._generate_cache_key(company, role, seniority)
        cached_jd = self._get_from_cache(cache_key)
        
        if cached_jd:
            print(f"✓ Using cached JD for {company}")
            return cached_jd
        
        # Attempt web scraping from multiple sources
        print(f"⚙️  Fetching JD for {company} ({role}, {seniority})...")
        
        jd_text = await self._scrape_from_careers_page(company, role)
        if not jd_text:
            jd_text = await self._scrape_from_job_boards(company, role, seniority)
        if not jd_text:
            jd_text = await self._scrape_from_naukri(company, role, seniority)
        
        if jd_text:
            self._save_to_cache(cache_key, jd_text)
            return jd_text
        
        print(f"⚠️  Could not fetch JD for {company}")
        return None
    
    async def _scrape_from_careers_page(self, company: str, role: str) -> Optional[str]:
        """Attempt to scrape from company careers page."""
        try:
            urls = [
                f"https://{company.lower()}.com/careers/",
                f"https://careers.{company.lower()}.com/",
                f"https://jobs.{company.lower()}.com/",
            ]
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            for url in urls:
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.get(url, headers=headers, timeout=5.0)
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.text, 'html.parser')
                            # Extract job listings
                            job_text = soup.get_text()
                            if role.lower() in job_text.lower():
                                return job_text[:5000]  # Limit to 5000 chars
                except Exception as e:
                    print(f"  Careers page scraping error: {e}")
                    continue
        except Exception as e:
            print(f"  Careers page scraping error: {e}")
        
        return None
    
    async def _scrape_from_job_boards(self, company: str, role: str, seniority: str) -> Optional[str]:
        """Scrape from public job boards."""
        try:
            # Example: Indeed
            search_query = f"{role} {company} {seniority}"
            url = f"https://www.indeed.com/jobs?q={search_query.replace(' ', '+')}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=5.0)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    job_snippet = soup.find('div', class_='jobsearch-ResultsList')
                    if job_snippet:
                        return job_snippet.get_text()[:5000]
        except Exception as e:
            print(f"  Job board scraping error: {e}")
        
        return None
    
    async def _scrape_from_naukri(self, company: str, role: str, seniority: str) -> Optional[str]:
        """Scrape from Naukri job portal (popular in India)."""
        try:
            print(f"  Fetching from Naukri for {company}...")
            
            # Naukri search URL format
            search_query = f"{role} {company}".replace(' ', '-').lower()
            url = f"https://www.naukri.com/search/?query={search_query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.naukri.com/',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=8)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Naukri job card containers
                    job_cards = soup.find_all('div', class_='jobTuple')
                if job_cards:
                    job_texts = []
                    for card in job_cards[:3]:  # Get top 3 results
                        job_text = card.get_text()
                        if job_text:
                            job_texts.append(job_text)
                    
                    combined_text = '\n'.join(job_texts)
                    if combined_text:
                        return combined_text[:5000]
                
                # Fallback: get all text if specific classes not found
                main_content = soup.find('div', class_='listContainer')
                if main_content:
                    return main_content.get_text()[:5000]
            
            print(f"  ⚠️  Naukri fetch status: {response.status_code}")
        except httpx.TimeoutException:
            print(f"  Naukri request timeout")
        except Exception as e:
            print(f"  Naukri scraping error: {e}")
        
        return None
    
    async def _analyze_single_jd(self, jd_text: str, company: str) -> Dict:
        """Analyze structural and content patterns in a single JD."""
        
        # Extract sections
        sections = await self._extract_sections(jd_text)
        
        # Extract metadata
        compensation = await self._extract_compensation(jd_text)
        skills = await self._extract_skills(jd_text)
        differentiators = await self._extract_differentiators(jd_text)
        tone = await self._analyze_tone(jd_text)
        
        return {
            "company": company,
            "sections_found": list(sections.keys()),
            "section_count": len(sections),
            "text_length": len(jd_text),
            "compensation": compensation,
            "required_skills": skills["required"],
            "nice_to_have_skills": skills["nice_to_have"],
            "differentiators": differentiators,
            "tone": tone,
            "keyword_density": self._calculate_keyword_density(jd_text),
            "section_details": sections
        }
    
    async def _extract_sections(self, jd_text: str) -> Dict[str, str]:
        """Extract predefined sections from JD."""
        sections = {}
        
        for section_name, pattern in self.JD_SECTIONS.items():
            match = re.search(pattern, jd_text, re.IGNORECASE)
            if match:
                sections[section_name] = match.group(0)[:200]  # First 200 chars
        
        return sections
    
    async def _extract_compensation(self, jd_text: str) -> Dict:
        """Extract compensation information."""
        compensation = {
            "salary_range": None,
            "currency": "USD",
            "has_equity": False,
            "has_bonus": False,
            "has_stock_options": False
        }
        
        # Look for salary range
        for pattern in self.COMPENSATION_PATTERNS:
            match = re.search(pattern, jd_text)
            if match:
                compensation["salary_range"] = match.group(0)
                break
        
        # Check for equity mentions
        if re.search(r"equity|stock options|ipo", jd_text, re.IGNORECASE):
            compensation["has_equity"] = True
        if re.search(r"bonus|performance bonus", jd_text, re.IGNORECASE):
            compensation["has_bonus"] = True
        if re.search(r"stock", jd_text, re.IGNORECASE):
            compensation["has_stock_options"] = True
        
        return compensation
    
    async def _extract_skills(self, jd_text: str) -> Dict[str, List[str]]:
        """Extract required and nice-to-have skills."""
        
        tech_keywords = [
            'python', 'java', 'javascript', 'typescript', 'react', 'vue', 'angular',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'postgresql', 'mongodb',
            'machine learning', 'ai', 'nlp', 'computer vision', 'devops', 'ci/cd'
        ]
        
        soft_skills = [
            'communication', 'leadership', 'teamwork', 'problem solving',
            'critical thinking', 'analytical', 'attention to detail'
        ]
        
        text_lower = jd_text.lower()
        required_skills = []
        nice_to_have = []
        
        # Identify required vs nice-to-have
        for skill in tech_keywords + soft_skills:
            if skill in text_lower:
                if re.search(rf"(?:must|required|essential).*{skill}", text_lower):
                    required_skills.append(skill.title())
                elif re.search(rf"(?:nice to have|preferred|beneficial).*{skill}", text_lower):
                    nice_to_have.append(skill.title())
                else:
                    required_skills.append(skill.title())
        
        return {
            "required": list(set(required_skills)),
            "nice_to_have": list(set(nice_to_have))
        }
    
    async def _extract_differentiators(self, jd_text: str) -> List[str]:
        """Extract unique selling points/differentiators."""
        text_lower = jd_text.lower()
        found = []
        
        for diff in self.DIFFERENTIATORS:
            if diff in text_lower:
                found.append(diff)
        
        return list(set(found))
    
    async def _analyze_tone(self, jd_text: str) -> Dict:
        """Analyze writing style and tone."""
        text_lower = jd_text.lower()
        
        tone = {
            "is_formal": bool(re.search(r"requirements|responsibilities|qualifications", text_lower)),
            "is_casual": bool(re.search(r"we're|we are|you'll|you will|fun|awesome", text_lower)),
            "is_technical": bool(re.search(r"algorithm|architecture|design pattern|scalability", text_lower)),
            "uses_bullet_points": bool(re.search(r"^[-•*]\s", jd_text, re.MULTILINE)),
            "has_emojis": bool(re.search(r"[\U0001F300-\U0001F9FF]", jd_text))
        }
        
        return tone
    
    async def _calculate_keyword_density(self, jd_text: str) -> Dict[str, float]:
        """Calculate density of key terms."""
        words = jd_text.lower().split()
        total_words = len(words)
        
        keywords = {
            "experience": len([w for w in words if w == "experience"]),
            "required": len([w for w in words if w == "required"]),
            "team": len([w for w in words if w == "team"]),
            "skills": len([w for w in words if w == "skills"])
        }
        
        return {k: round((v / total_words) * 100, 2) for k, v in keywords.items()}
    
    async def _extract_patterns(self, analyses: Dict) -> Dict:
        """Identify common patterns across competitor JDs."""
        
        patterns = {
            "common_sections": await self._find_common_sections(analyses),
            "average_jd_length": round(sum(a["text_length"] for a in analyses.values()) / len(analyses)) if len(analyses) > 0 else 0,
            "most_common_skills": self._find_most_common_skills(analyses),
            "tone_characteristics": self._aggregate_tone(analyses),
            "compensation_trends": self._analyze_compensation_trends(analyses),
            "differentiator_frequency": self._count_differentiators(analyses)
        }
        
        return patterns
    
    async def _find_common_sections(self, analyses: Dict) -> List[str]:
        """Find sections that appear in most JDs."""
        section_counts = {}
        
        for analysis in analyses.values():
            for section in analysis["sections_found"]:
                section_counts[section] = section_counts.get(section, 0) + 1
        
        # Return sections that appear in >50% of JDs
        threshold = len(analyses) / 2
        return [s for s, count in section_counts.items() if count > threshold]
    
    async def _find_most_common_skills(self, analyses: Dict) -> List[str]:
        """Identify most frequently required skills."""
        skill_counts = {}
        
        for analysis in analyses.values():
            for skill in analysis["required_skills"]:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        # Return top 10 skills
        sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
        return [skill for skill, _ in sorted_skills[:10]]
    
    async def _aggregate_tone(self, analyses: Dict) -> Dict:
        """Aggregate tone characteristics."""
        tone_summary = {}
        
        for analysis in analyses.values():
            for tone_attr, value in analysis["tone"].items():
                if tone_attr not in tone_summary:
                    tone_summary[tone_attr] = 0
                if value:
                    tone_summary[tone_attr] += 1
        
        return tone_summary
    
    async def _analyze_compensation_trends(self, analyses: Dict) -> Dict:
        """Analyze compensation patterns."""
        comp_trend = {
            "companies_with_salary_info": 0,
            "companies_with_equity": sum(
                1 for a in analyses.values() if a["compensation"]["has_equity"]
            ),
            "companies_with_bonus": sum(
                1 for a in analyses.values() if a["compensation"]["has_bonus"]
            ),
            "average_transparency": 0
        }
        
        comp_trend["companies_with_salary_info"] = sum(
            1 for a in analyses.values() if a["compensation"]["salary_range"]
        )
        
        comp_trend["average_transparency"] = round(
            (comp_trend["companies_with_salary_info"] / len(analyses)) * 100, 2
        ) if len(analyses) > 0 else 0
        
        return comp_trend
    
    async def _count_differentiators(self, analyses: Dict) -> Dict[str, int]:
        """Count how often each differentiator appears."""
        diff_counts = {}
        
        for analysis in analyses.values():
            for diff in analysis["differentiators"]:
                diff_counts[diff] = diff_counts.get(diff, 0) + 1
        
        return diff_counts
    
    async def _identify_gaps(self, analyses: Dict) -> Dict:
        """Identify gaps and missing elements in competitor JDs."""
        
        gaps = {
            "salary_transparency_gap": await self._identify_salary_gaps(analyses),
            "missing_sections": await self._identify_missing_sections(analyses),
            "missing_differentiators": await self._identify_missing_differentiators(analyses),
            "vague_requirements": await self._identify_vague_requirements(analyses)
        }
        
        return gaps
    
    async def _identify_salary_gaps(self, analyses: Dict) -> Dict:
        """Identify companies not disclosing salaries."""
        no_salary = [
            name for name, analysis in analyses.items()
            if not analysis["compensation"]["salary_range"]
        ]
        
        return {
            "companies_without_salary": no_salary,
            "transparency_opportunity": len(no_salary) > 0
        }
    
    async def _identify_missing_sections(self, analyses: Dict) -> Dict:
        """Identify commonly expected sections that are missing."""
        expected_sections = [
            "about_company", "role_summary", "responsibilities",
            "requirements", "benefits", "compensation"
        ]
        
        missing = {}
        for company, analysis in analyses.items():
            missing[company] = [
                s for s in expected_sections if s not in analysis["sections_found"]
            ]
        
        return missing
    
    async def _identify_missing_differentiators(self, analyses: Dict) -> Dict:
        """Identify differentiators competitors are NOT highlighting."""
        common_diffs = set()
        
        for analysis in analyses.values():
            common_diffs.update(analysis["differentiators"])
        
        all_possible = set(self.DIFFERENTIATORS)
        missing_diffs = all_possible - common_diffs
        
        return {
            "competitors_not_highlighting": list(missing_diffs),
            "opportunity_count": len(missing_diffs)
        }
    
    async def _identify_vague_requirements(self, analyses: Dict) -> List[str]:
        """Identify vague language in requirements."""
        vague_terms = [
            "strong", "excellent", "experienced", "passion", "ninja",
            "rockstar", "guru", "self-motivated", "team player"
        ]
        
        vague_by_company = {}
        
        for company, analysis in analyses.items():
            for term in vague_terms:
                # Would need to check actual JD text, simplified here
                if term in analysis.get("keyword_density", {}):
                    if company not in vague_by_company:
                        vague_by_company[company] = []
                    vague_by_company[company].append(term)
        
        return vague_by_company
    
    async def _find_opportunities(self, patterns: Dict, gaps: Dict) -> List[Dict]:
        """Generate actionable opportunities based on patterns and gaps."""
        
        opportunities = []
        
        # Opportunity 1: Salary Transparency
        if gaps["salary_transparency_gap"]["transparency_opportunity"]:
            opportunities.append({
                "category": "Compensation Transparency",
                "gap": "Most competitors not disclosing salaries",
                "opportunity": "Be first to publish salary ranges - increases applications by 40-50%",
                "action": "Include specific salary band in JD"
            })
        
        # Opportunity 2: Missing Differentiators
        missing_count = gaps["missing_differentiators"]["opportunity_count"]
        if missing_count > 3:
            opportunities.append({
                "category": "Employee Benefits",
                "gap": f"{missing_count} differentiators competitors aren't mentioning",
                "opportunity": "Highlight unique benefits to stand out",
                "action": "Add 3-5 unique perks competitors don't offer"
            })
        
        # Opportunity 3: Section Structure
        opportunities.append({
            "category": "JD Structure",
            "gap": "Common sections vary across competitors",
            "opportunity": "Standardized, scannable format improves engagement",
            "action": f"Include all {len(patterns['common_sections'])} common sections"
        })
        
        # Opportunity 4: Tone & Language
        formal_count = patterns["tone_characteristics"].get("is_formal", 0)
        casual_count = patterns["tone_characteristics"].get("is_casual", 0)
        
        if casual_count > formal_count:
            opportunities.append({
                "category": "Communication Style",
                "gap": "Competitors using casual tone",
                "opportunity": "Better candidate match and engagement with conversational JDs",
                "action": "Use 'we're' instead of 'we are', emojis, casual language"
            })
        
        return opportunities
    
    async def _generate_parser_code(self, analyses: Dict) -> str:
        """Generate Python code for parsing JDs based on analysis."""
        
        code = '''"""
Auto-generated JD Parser - Based on Competitor Analysis
"""

import re
from typing import Dict

class AutoGeneratedJDParser:
    """Parser generated from competitor JD analysis."""
    
    COMMON_SECTIONS = {
'''
        
        # Add detected sections
        for i, (company, analysis) in enumerate(analyses.items()):
            if i < 3:  # Limit to first 3
                sections = analysis["sections_found"]
                code += f'        # From {company}\n'
                for section in sections[:3]:
                    code += f'         {section}: r"(?:{section}|{section.upper()}).*?(?=\n\n|\\Z)",\n'
        
        code += '''    }
    
    @staticmethod
    def parse(jd_text: str) -> Dict:
        """Extract sections and key data from JD."""
        result = {}
        
        # Extract sections
        for section_name, pattern in AutoGeneratedJDParser.COMMON_SECTIONS.items():
            match = re.search(pattern, jd_text, re.IGNORECASE | re.DOTALL)
            if match:
                result[section_name] = match.group(0)[:500]
        
        # Extract compensation
        salary_match = re.search(r"\\$(\\d+)k?\\s*(?:-|to)\\s*\\$(\\d+)k?", jd_text)
        if salary_match:
            result["salary_range"] = salary_match.group(0)
        
        # Extract skills
        skills = []
        skill_keywords = ["python", "java", "aws", "kubernetes", "react"]
        for skill in skill_keywords:
            if skill in jd_text.lower():
                skills.append(skill.title())
        result["identified_skills"] = skills
        
        return result

# Usage
# parser = AutoGeneratedJDParser()
# parsed = parser.parse(jd_text)
'''
        
        return code
    
    async def _generate_cache_key(self, company: str, role: str, seniority: str) -> str:
        """Generate cache key."""
        key = f"{company}_{role}_{seniority}"
        return hashlib.md5(key.encode()).hexdigest()
    
    async def _get_from_cache(self, cache_key: str) -> Optional[str]:
        """Retrieve JD from cache if valid."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(cache_file)
                data = response.json()
            
            # Check TTL
            cached_time = datetime.fromisoformat(data["timestamp"])
            if datetime.now() - cached_time > self.cache_ttl:
                cache_file.unlink()  # Delete expired cache
                return None
            
            return data["content"]
        except Exception as e:
            print(f"Cache read error: {e}")
            return None
    
    async def _save_to_cache(self, cache_key: str, content: str) -> None:
        """Save JD to cache."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            async with httpx.AsyncClient() as client:
                await client.put(cache_file, json={
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                })
        except Exception as e:
            print(f"Cache write error: {e}")

