from agents.jd_arcitecture_agent.tools.legal_requirements_checker_tool import LegalRequirementsCheckerTool
from agents.jd_arcitecture_agent.tools.jd_formatter_and_poster_tool import JDPosterTool
from agents.jd_arcitecture_agent.tools.skills_extractor import SkillsExtractorTool
from agents.jd_arcitecture_agent.tools.competitor_analyzer import CompetitorJDAnalyzerTool
from agents.jd_arcitecture_agent.tools.salary_benchmark_tool import SalaryBenchMarkerTool
from agents.jd_arcitecture_agent.tools.dei_language_auditor_tool import DEILanguageTool

__tools__ = [
    LegalRequirementsCheckerTool(),
    JDPosterTool(),
    SkillsExtractorTool(),
    CompetitorJDAnalyzerTool(),
    SalaryBenchMarkerTool(),
    DEILanguageTool()
]

