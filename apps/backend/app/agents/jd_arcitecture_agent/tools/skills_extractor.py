"""
Free Skill Extractor Tool - No API keys required! (Asynchronous Version)
Extracts must-have vs nice-to-have skills from job descriptions and GitHub repositories.
"""

import httpx 
import re
from typing import List, Dict, Type, ClassVar
from pydantic import ConfigDict
from crewai.tools import BaseTool
from agents.jd_arcitecture_agent.schema.research_schema import (
    SkillExtractorArgs,
    SkillExtractorOutput,
)

class SkillsExtractorTool(BaseTool):
    """Extract skills from job descriptions and GitHub repos using free APIs asynchronously."""
    name: str = "SkillsExtractor"
    description: str = (
        "Use this tool to extract must-have and nice-to-have skills from job descriptions and GitHub repositories. "
        "The tool identifies technical skills, tools, and concepts relevant to the specified role and domain."
    )
    args_schema: Type[SkillExtractorArgs] = SkillExtractorArgs
    output_schema: Type[SkillExtractorOutput] = SkillExtractorOutput
    
    model_config = ConfigDict(arbitrary_types_allowed=True, extra='allow')

    SKILL_DATABASE: ClassVar[Dict] = {
        "Technology": {
            "programming_languages": ["Python", "Java", "JavaScript", "TypeScript"],
            "frameworks": ["Django", "FastAPI", "React"],
            "databases": ["PostgreSQL", "MongoDB"],
            "tools": ["Docker", "Kubernetes", "Git"]
        }
    }

    # --- MAIN FLOW ENGINE (ASYNC) ---
    async def _run(self, role: str, domain: str, source: str) -> SkillExtractorOutput:
        """Extract skills from job description and GitHub repos natively using async."""
        
        # 2. CHANGE: Removed 'await' because text extraction is pure local calculation now
        text_skills = self._extract_from_text(source) 
        
        # This performs real network HTTP requests, so 'await' is critically required
        github_skills = await self._extract_from_github(role, domain)
        
        domain_skills = self.SKILL_DATABASE.get(domain, {})
        
        # Assumed helper functions (pure local calculations, do not use await)
        must_have = self._categorize_must_have(text_skills, domain_skills)
        nice_to_have = self._categorize_nice_to_have(text_skills, domain_skills)
        anti_patterns = self._extract_anti_patterns(source)
        emerging = self._extract_emerging_skills(text_skills + github_skills)
        
        return {
            "must_have_skills": must_have,
            "good_to_have_skills": nice_to_have,
            "anti_pattern_skills": anti_patterns,
            "emerging_skills": emerging,
            "github_skills": github_skills
        }
        
    # 3. CHANGE: Removed 'async' from this method because it is a pure local calculation
    def _extract_from_text(self, source: str) -> List[str]:
        """Extract technical skills from source text using pattern matching synchronously."""
        skills = []
        source_lower = source.lower()
        
        patterns = [
            r'(?:expertise|experience|proficiency)\s+(?:in|with|using)\s+([a-zA-Z0-9+#\s,.\-]+)',
            r'([A-Z][a-zA-Z0-9+#.\-]*)\s+(?:experience|developer|engineer|specialist)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, source, re.IGNORECASE)
            for match in matches:
                skills.extend([s.strip() for s in match.split(',') if s.strip()])
        
        tech_keywords = ['python', 'java', 'javascript', 'typescript', 'react', 'fastapi']
        for keyword in tech_keywords:
            if keyword in source_lower:
                skills.append(keyword.title())
        
        return list(set(skills))

    # --- THE NETWORK API NODE (TRULY ASYNC) ---
    async def _extract_from_github(self, role: str, domain: str) -> List[str]:
        """Fetch skills from GitHub repositories using non-blocking HTTP requests."""
        skills = []
        
        # 4. CHANGE: Created an async HTTP client session context
        async with httpx.AsyncClient() as client:
            try:
                search_query = f"{role} {domain}".replace(" ", "+")
                url = f"https://api.github.com/search/repositories?q={search_query}&sort=stars&per_page=5"
                
                headers = {
                    'Accept': 'application/vnd.github.v3+json',
                    'User-Agent': 'SkillExtractor'
                }
                
                # 5. CHANGE: Swapped to 'await client.get' instead of 'requests.get'
                response = await client.get(url, headers=headers, timeout=5.0)
                
                if response.status_code == 200:
                    repos = response.json().get('items', [])
                    
                    for repo in repos[:3]:  # Analyze top 3 repos
                        readme_url = f"https://raw.githubusercontent.com/{repo['full_name']}/main/README.md"
                        
                        # 6. CHANGE: Async raw README file download
                        readme_response = await client.get(readme_url, timeout=5.0)
                        
                        if readme_response.status_code != 200:
                            readme_url = f"https://raw.githubusercontent.com/{repo['full_name']}/master/README.md"
                            readme_response = await client.get(readme_url, timeout=5.0)
                        
                        if readme_response.status_code == 200:
                            readme_text = readme_response.text.lower()
                            
                            tech_keywords = ['python', 'javascript', 'typescript', 'java', 'fastapi']
                            for keyword in tech_keywords:
                                if keyword in readme_text:
                                    skills.append(keyword.title())
                                    
            except Exception as e:
                print(f"Async Tool Error fetching from GitHub: {e}")
                
        return list(set(skills))


    async def _categorize_must_have(self, text_skills: List[str], domain_skills: Dict) -> List[str]:
        """Categorize skills as must-have (core requirements)."""
        must_have = []
        all_domain_skills = []
        
        for category_skills in domain_skills.values():
            all_domain_skills.extend(category_skills)
        
        # Must-have: frequently mentioned + technical specificity
        for skill in text_skills:
            if any(skill.lower() in ds.lower() or ds.lower() in skill.lower() for ds in all_domain_skills):
                must_have.append(skill)
        
        # Add core domain skills if not already present
        for lang in domain_skills.get('programming_languages', [])[:2]:
            if lang not in must_have:
                must_have.append(lang)
        
        return list(set(must_have))[:10]

    async def _categorize_nice_to_have(self, text_skills: List[str], domain_skills: Dict) -> List[str]:
        """Categorize skills as nice-to-have (complementary skills)."""
        nice_to_have = []
        
        # Nice-to-have: tools and concepts
        nice_to_have.extend(domain_skills.get('tools', [])[:3])
        nice_to_have.extend(domain_skills.get('concepts', [])[:2])
        
        return list(set(nice_to_have))[:8]

    async def _extract_anti_patterns(self, source: str) -> List[str]:
        """Extract vague terms (anti-patterns) from text."""
        found_anti_patterns = []
        source_lower = source.lower()
        
        for anti_pattern in self.ANTI_PATTERNS:
            if anti_pattern in source_lower:
                found_anti_patterns.append(anti_pattern)
        
        return found_anti_patterns if found_anti_patterns else ["✓ No vague terms detected"]

    async def _extract_emerging_skills(self, skills: List[str]) -> List[str]:
        """Extract emerging skills that are trending."""
        emerging = []
        skills_lower = [s.lower() for s in skills]
        
        for emerging_skill in self.EMERGING_SKILLS:
            if any(emerging_skill.lower() in s for s in skills_lower):
                emerging.append(emerging_skill)
        
        return emerging if emerging else ["📈 Trending: AI/ML, Cloud-Native, IaC"]

