from agents.JD_Arcitecture_agent.tools.legal_requirements_checker_tool import LegalRequirementsCheckerTool
from agents.JD_Arcitecture_agent.tools.jd_formatter_and_poster_tool import JDPosterTool
from agents.JD_Arcitecture_agent.tools.skills_extractor import SkillsExtractorTool
from agents.JD_Arcitecture_agent.tools.competitor_analyzer import CompetitorJDAnalyzerTool
from agents.JD_Arcitecture_agent.tools.salary_benchmark_tool import SalaryBenchMarkerTool
from agents.JD_Arcitecture_agent.tools.dei_language_auditor_tool import DEILanguageTool

__tools__ = [
    LegalRequirementsCheckerTool(),
    JDPosterTool(),
    SkillsExtractorTool(),
    CompetitorJDAnalyzerTool(),
    SalaryBenchMarkerTool(),
    DEILanguageTool()
]