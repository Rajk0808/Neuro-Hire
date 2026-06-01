from apps.backend.app.agents.JD_Arcitecture_agent.tools.legal_requirements_checker_tool import LegalRequirementsCheckerTool
from apps.backend.app.agents.JD_Arcitecture_agent.tools.jd_formatter_and_poster_tool import JDPosterTool
from apps.backend.app.agents.JD_Arcitecture_agent.tools.skills_extractor import SkillsExtractorTool
from apps.backend.app.agents.JD_Arcitecture_agent.tools.competitor_analyzer import CompetitorJDAnalyzerTool
from apps.backend.app.agents.JD_Arcitecture_agent.tools.salary_benchmark_tool import SalaryBenchMarkerTool
from apps.backend.app.agents.JD_Arcitecture_agent.tools.dei_language_auditor_tool import DEILanguageTool

__tools__ = [
    LegalRequirementsCheckerTool(),
    JDPosterTool(),
    SkillsExtractorTool(),
    CompetitorJDAnalyzerTool(),
    SalaryBenchMarkerTool(),
    DEILanguageTool()
]