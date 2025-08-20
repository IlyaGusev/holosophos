import logging
from typing import Optional

from codearkt.codeact import CodeActAgent, Prompts
from codearkt.llm import LLM

from holosophos.files import PROMPTS_DIR_PATH


NAME = "proposer"
DESCRIPTION = """This team member generates creative ideas for research experiments.
He analyzes existing ideas and proposes new research directions, assessing their interestingness, feasibility, and novelty.
Ask him when you need to come up with new experiments or research approaches.
Provide a detailed task description and context as an argument, as well as the arxiv_id of the baseline paper."""


def get_proposer_agent(
    model: LLM,
    max_iterations: int = 10,
    planning_interval: Optional[int] = 3,
    verbosity_level: int = logging.INFO,
) -> CodeActAgent:
    prompts = Prompts.load(PROMPTS_DIR_PATH / "proposer.yaml")
    return CodeActAgent(
        name=NAME,
        description=DESCRIPTION,
        tool_names=[
            "academia_web_search",
            "academia_visit_webpage",
            "academia_document_qa",
            "academia_extract_bitflip_info",
            "academia_generate_research_proposal",
            "academia_score_research_proposals",
        ],
        llm=model,
        max_iterations=max_iterations,
        planning_interval=planning_interval,
        prompts=prompts,
        verbosity_level=verbosity_level,
    )
