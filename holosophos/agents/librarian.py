from codearkt.codeact import CodeActAgent, Prompts
from codearkt.llm import LLM

from holosophos.files import PROMPTS_DIR_PATH

NAME = "librarian"
DESCRIPTION = """This team member runs gets and analyzes information from papers.
He has access to ArXiv, Semantic Scholar, ACL Anthology, and web search.
Ask him any questions about papers and web articles.
Give him your task as an argument. Follow the task format described above, include all the details."""


def get_librarian_agent(model_name: str) -> CodeActAgent:
    llm = LLM(model_name=model_name)
    prompts = Prompts.load(PROMPTS_DIR_PATH / "librarian.json")
    return CodeActAgent(
        name=NAME,
        description=DESCRIPTION,
        llm=llm,
        prompts=prompts,
        tool_names=[
            "academia_arxiv_download",
            "academia_arxiv_search", 
            "academia_anthology_search",
            "academia_s2_citations",
            "academia_hf_datasets_search",
            # "academia_document_qa",
            "exa_web_search_exa",
            "exa_crawling_exa",
        ],
        planning_interval=5,
    )
    
