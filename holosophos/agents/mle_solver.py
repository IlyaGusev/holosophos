from codearkt.codeact import CodeActAgent, Prompts
from codearkt.llm import LLM

from holosophos.files import PROMPTS_DIR_PATH


NAME = "mle_solver"
DESCRIPTION = """This team member is an egineer that writes code and runs computational experiments using remote GPUs.
He has access to tools that write and execute code on a remote GPU.
Ask him when you need to solve any programming tasks that require GPU.
Give him your detailed task as an argument. Follow the task format described above, include all the details."""


def get_mle_solver_agent(model_name: str) -> CodeActAgent:
    llm = LLM(model_name=model_name)
    prompts = Prompts.load(PROMPTS_DIR_PATH / "mle_solver.yaml")
    return CodeActAgent(
        name=NAME,
        description=DESCRIPTION,
        llm=llm,
        prompts=prompts,
        tool_names=[
            "mle_kit_remote_bash",
            "mle_kit_remote_text_editor", 
            "mle_kit_remote_download",
            "academia_hf_datasets_search",
            "exa_web_search_exa",
            "exa_crawling_exa",
        ],
        planning_interval=7,
    )
