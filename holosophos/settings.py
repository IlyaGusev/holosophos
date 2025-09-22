import logging
from typing import Optional, Sequence

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MODEL_NAME: str = "deepseek/deepseek-chat-v3-0324"
    MAX_COMPLETION_TOKENS: int = 8192
    MAX_HISTORY_TOKENS: int = 131072

    ACADEMIA_MCP_URL: str = "http://0.0.0.0:5056/mcp"
    MLE_KIT_MCP_URL: str = "http://0.0.0.0:5057/mcp"

    ENABLE_PHOENIX: bool = False
    PHOENIX_URL: str = "http://localhost:6006"
    PHOENIX_PROJECT_NAME: str = "holosophos"
    PHOENIX_ENDPOINT: Optional[str] = None

    PORT: int = 5055
    WORKSPACE_DIR: str = "./workdir"

    VERBOSITY_LEVEL: int = logging.INFO

    MANAGER_MAX_ITERATIONS: int = 100
    MANAGER_PLANNING_INTERVAL: int = 9
    MANAGER_TOOLS: Sequence[str] = (
        "bash",
        "text_editor",
        "describe_image",
        "speech_to_text",
    )

    LIBRARIAN_MAX_ITERATIONS: int = 100
    LIBRARIAN_PLANNING_INTERVAL: int = 9
    LIBRARIAN_TOOLS: Sequence[str] = (
        "arxiv_download",
        "arxiv_search",
        "anthology_search",
        "s2_get_citations",
        "s2_get_references",
        "s2_corpus_id_from_arxiv_id",
        "s2_get_info",
        "hf_datasets_search",
        "document_qa",
        "web_search",
        "visit_webpage",
        "text_editor",
        "describe_image",
    )

    MLE_SOLVER_MAX_ITERATIONS: int = 200
    MLE_SOLVER_PLANNING_INTERVAL: int = 14
    MLE_SOLVER_TOOLS: Sequence[str] = (
        "remote_bash",
        "remote_text_editor",
        "remote_download",
        "llm_proxy_remote",
        "hf_datasets_search",
        "web_search",
        "visit_webpage",
        "describe_image",
    )

    WRITER_MAX_ITERATIONS: int = 100
    WRITER_PLANNING_INTERVAL: int = 9
    WRITER_TOOLS: Sequence[str] = (
        "get_latex_template",
        "get_latex_templates_list",
        "compile_latex",
        "bash",
        "text_editor",
        "read_pdf",
        "describe_image",
    )

    PROPOSER_MAX_ITERATIONS: int = 200
    PROPOSER_PLANNING_INTERVAL: int = 9
    PROPOSER_TOOLS: Sequence[str] = (
        "web_search",
        "visit_webpage",
        "document_qa",
        "extract_bitflip_info",
        "generate_research_proposals",
        "score_research_proposals",
        "text_editor",
    )

    REVIEWER_MAX_ITERATIONS: int = 50
    REVIEWER_PLANNING_INTERVAL: int = 9
    REVIEWER_TOOLS: Sequence[str] = (
        "review_pdf_paper",
        "download_pdf_paper",
        "visit_webpage",
        "web_search",
        "bash",
        "text_editor",
        "describe_image",
    )

    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="", case_sensitive=False, extra="ignore"
    )

    @property
    def RESOLVED_PHOENIX_ENDPOINT(self) -> str:
        if self.PHOENIX_ENDPOINT:
            return str(self.PHOENIX_ENDPOINT)
        return f"{self.PHOENIX_URL}/v1/traces"


settings = Settings()
