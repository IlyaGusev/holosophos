from codearkt.codeact import CodeActAgent, Prompts
from codearkt.llm import LLM

from holosophos.files import PROMPTS_DIR_PATH


NAME = "proposer"
DESCRIPTION = """This team member generates creative ideas for research experiments.
He analyzes existing ideas and proposes new research directions, assessing their interestingness, feasibility, and novelty.
Ask him when you need to come up with new experiments or research approaches.
Provide a detailed task description and context as an argument."""


def get_proposer_agent(model_name: str) -> CodeActAgent:
    llm = LLM(model_name=model_name)
    prompts = Prompts.load(PROMPTS_DIR_PATH / "proposer.json")
    return CodeActAgent(
        name=NAME,
        description=DESCRIPTION,
        llm=llm,
        prompts=prompts,
        tool_names=[
            # "academia_document_qa",
            "exa_web_search_exa",
            "exa_crawling_exa",
        ],
        planning_interval=7,
    )
