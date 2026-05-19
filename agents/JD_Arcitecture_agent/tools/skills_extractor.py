"""
Free Skill Extractor Tool - No API keys required!
Extracts must-have vs nice-to-have skills from job descriptions and GitHub repositories.
"""

import requests
import re
from typing import List, Dict
from agents.JD_Arcitecture_agent.schema.research_schema import (
    SkillExtractorArgs,
    SkillExtractorOutput,
)
from crewai.tools import BaseTool

class FreeSkillsExtractor(BaseTool):
    """Extract skills from job descriptions and GitHub repos using free APIs."""
    
    # Comprehensive skill database by domain
    SKILL_DATABASE = {
        "Technology": {
            "programming_languages": ["Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust", "PHP", "Ruby", "Swift", "Kotlin"],
            "frameworks": ["Django", "FastAPI", "Flask", "React", "Vue.js", "Angular", "Next.js", "Spring", "ASP.NET", "Rails", "Laravel"],
            "databases": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "DynamoDB", "Elasticsearch", "Cassandra", "Neo4j"],
            "tools": ["Docker", "Kubernetes", "Git", "AWS", "Azure", "GCP", "Jenkins", "GitLab CI", "GitHub Actions"],
            "concepts": ["REST API", "GraphQL", "Microservices", "CI/CD", "DevOps", "Cloud Computing", "Agile"]
        },
        "Data Science": {
            "programming_languages": ["Python", "R", "SQL", "Scala"],
            "frameworks": ["TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy", "Matplotlib", "Seaborn"],
            "tools": ["Jupyter", "Tableau", "Power BI", "Apache Spark", "Hadoop", "AWS SageMaker"],
            "concepts": ["Machine Learning", "Deep Learning", "NLP", "Computer Vision", "Data Analysis", "Statistics"]
        }
    }

    # Anti-patterns (vague terms to avoid in job descriptions)
    ANTI_PATTERNS = [
        "guru", "ninja", "rockstar", "wizard", "magic", "excellent communication",
        "strong work ethic", "team player", "hard-working", "self-motivated",
        "proactive", "detail-oriented", "passionate", "smart"
    ]

    # Emerging skills gaining traction
    EMERGING_SKILLS = [
        "AI/ML", "LLMs", "Prompt Engineering", "Vector Databases", "Edge Computing",
        "Quantum Computing", "Web3", "Blockchain", "GraphQL", "WebAssembly",
        "Rust", "Go", "Terraform", "Infrastructure as Code", "GitOps"
    ]

    def _run(self, args: SkillExtractorArgs) -> SkillExtractorOutput:
        """
        Extract skills from job description and GitHub repos.
        
        Args:
            args: SkillExtractorArgs containing role, domain, and source
        """
        
        # Extract skills from source text
        text_skills = self._extract_from_text(args.source)
        
        # Get GitHub repo data
        github_skills = self._extract_from_github(args.role, args.domain)
        
        # Get domain-specific skills
        domain_skills = self.SKILL_DATABASE.get(args.domain, {})
        
        # Categorize skills
        must_have = self._categorize_must_have(text_skills, domain_skills)
        nice_to_have = self._categorize_nice_to_have(text_skills, domain_skills)
        anti_patterns = self._extract_anti_patterns(args.source)
        emerging = self._extract_emerging_skills(text_skills + github_skills)
        
        return {
            "must_have_skills": must_have,
            "nice_to_have_skills": nice_to_have,
            "anti_pattern_skills": anti_patterns,
            "emerging_skills": emerging,
            "github_skills": github_skills
        }

    def _extract_from_text(self, source: str) -> List[str]:
        """Extract technical skills from source text using pattern matching."""
        skills = []
        source_lower = source.lower()
        
        # Pattern-based extraction
        patterns = [
            r'(?:expertise|experience|proficiency)\s+(?:in|with|using)\s+([a-zA-Z0-9+#\s,.\-]+)',
            r'([A-Z][a-zA-Z0-9+#.\-]*)\s+(?:experience|developer|engineer|specialist)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, source, re.IGNORECASE)
            for match in matches:
                skills.extend([s.strip() for s in match.split(',') if s.strip()])
        
        # Look for specific technical keywords
        tech_keywords = [
            'python', 'java', 'javascript', 'typescript', 'react', 'vue', 'angular',
            'django', 'flask', 'fastapi', 'node.js', 'docker', 'kubernetes',
            'postgres', 'postgresql', 'mongodb', 'redis', 'aws', 'gcp', 'azure', 'git',
            'rest api', 'graphql', 'microservices', 'sql', 'nosql', 'devops',
            'ci/cd', 'terraform', 'jenkins', 'machine learning', 'tensorflow',
            'pytorch', 'nlp', 'cloud', 'oop', 'design patterns', 'agile', 'scrum'
        ]
        
        for keyword in tech_keywords:
            if keyword in source_lower:
                skills.append(keyword.title())
        
        return list(set(skills))

    def _extract_from_github(self, role: str, domain: str) -> List[str]:
        """Fetch skills from GitHub repositories using free GitHub API."""
        skills = []
        
        try:
            # Search for GitHub repos related to the role
            search_query = f"{role} {domain}".replace(" ", "+")
            url = f"https://api.github.com/search/repositories?q={search_query}&sort=stars&per_page=5"
            
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'SkillExtractor'
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                repos = response.json().get('items', [])
                
                for repo in repos[:3]:  # Analyze top 3 repos
                    # Get README content
                    readme_url = f"https://raw.githubusercontent.com/{repo['full_name']}/main/README.md"
                    readme_response = requests.get(readme_url, timeout=5)
                    
                    if readme_response.status_code != 200:
                        # Try master branch if main doesn't exist
                        readme_url = f"https://raw.githubusercontent.com/{repo['full_name']}/master/README.md"
                        readme_response = requests.get(readme_url, timeout=5)
                    
                    if readme_response.status_code == 200:
                        readme_text = readme_response.text.lower()
                        
                        # Extract tech keywords from README
                        tech_keywords = [
                            'python', 'javascript', 'typescript', 'java', 'cpp', 'c++', 'rust',
                            'react', 'vue', 'angular', 'django', 'fastapi', 'spring',
                            'docker', 'kubernetes', 'aws', 'azure', 'postgresql', 'mongodb',
                            'nodejs', 'node.js', 'go', 'ruby', 'php', 'scala'
                        ]
                        
                        for keyword in tech_keywords:
                            if keyword in readme_text:
                                skills.append(keyword.title().replace('C++', 'C++'))
        
        except Exception as e:
            print(f"GitHub extraction note: {e}")
        
        return list(set(skills))

    def _categorize_must_have(self, text_skills: List[str], domain_skills: Dict) -> List[str]:
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

    def _categorize_nice_to_have(self, text_skills: List[str], domain_skills: Dict) -> List[str]:
        """Categorize skills as nice-to-have (complementary skills)."""
        nice_to_have = []
        
        # Nice-to-have: tools and concepts
        nice_to_have.extend(domain_skills.get('tools', [])[:3])
        nice_to_have.extend(domain_skills.get('concepts', [])[:2])
        
        return list(set(nice_to_have))[:8]

    def _extract_anti_patterns(self, source: str) -> List[str]:
        """Extract vague terms (anti-patterns) from text."""
        found_anti_patterns = []
        source_lower = source.lower()
        
        for anti_pattern in self.ANTI_PATTERNS:
            if anti_pattern in source_lower:
                found_anti_patterns.append(anti_pattern)
        
        return found_anti_patterns if found_anti_patterns else ["✓ No vague terms detected"]

    def _extract_emerging_skills(self, skills: List[str]) -> List[str]:
        """Extract emerging skills that are trending."""
        emerging = []
        skills_lower = [s.lower() for s in skills]
        
        for emerging_skill in self.EMERGING_SKILLS:
            if any(emerging_skill.lower() in s for s in skills_lower):
                emerging.append(emerging_skill)
        
        return emerging if emerging else ["📈 Trending: AI/ML, Cloud-Native, IaC"]
