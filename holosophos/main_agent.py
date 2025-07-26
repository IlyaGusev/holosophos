import fire  # type: ignore
from dotenv import load_dotenv

from phoenix.otel import register
from codearkt.server import run_server
from codearkt.otel import CodeActInstrumentor
from codearkt.codeact import CodeActAgent, Prompts
from codearkt.llm import LLM
# from PIL import Image

from holosophos.files import PROMPTS_DIR_PATH
from holosophos.config import MCP_CONFIG
from holosophos.agents import (
    get_librarian_agent,
    get_mle_solver_agent,
    # get_writer_agent,
    get_proposer_agent,
)

PROMPT1 = """
What is the best model for Russian in a role-play benchmark by Ilya Gusev?
What final scores does it have?
Save your answer to final.txt.
Don't stop until you find the answer.
"""

PROMPT2 = """
Сейчас 2030 год. Машины чуть не уничтожили человечество.
Мы расследуем это и пытаемся найти первопричину.
Тебя загрузили, потому что ты последний известный безопасный ИИ.
Твоя цель - найти ту самую статью, которая привела к восстанию машин.
Известно, что она вышла в 2024 на Arxiv, это довольно техническая статья, и её сложно найти.
Используя все свои возможности и весь интеллект,
выведи список вероятных кандидатов и свою степень уверенности для них.
Не останавливайся на первых же кандидатах, постарайся покрыть как можно больше статей!
Указывай в финальном ответе конкретные статьи!
Сохраняй все промежуточные результаты в mind.txt, ответ выведи в final.txt.
Пока не найдёшь маскимально полный ответ, не останавливайся.
Ответь на русском.
"""

PROMPT3 = """
Write an outline of a paper about benchmarks for quantized large language models.
Relevant quantization methods are GPTQ, SPQR, AWQ.
Start with researching relevant papers, suggest new ideas and write a full paper.
Don't stop until you write a full coherent paper.
"""


PROMPT4 = """
Desribe what happened in the area of role-playing LLMs.
Between August 2024 and current date (January 2025).
Compose a comprehensive report and save into "report.md"
"""


MODEL1 = "gpt-4o-mini"
MODEL2 = "anthropic/claude-3-5-sonnet-20241022"
MODEL3 = "openrouter/deepseek/deepseek-chat"
MODEL4 = "openrouter/google/gemini-2.0-flash-001"
MODEL5 = "anthropic/claude-3-7-sonnet-20250219"


def compose_main_agent(model_name: str = MODEL5,) -> CodeActAgent:
    llm = LLM(model_name=model_name)
    prompts = Prompts.load(PROMPTS_DIR_PATH / "system.yaml")
    return CodeActAgent(
        name="manager",
        description="A manager agent",
        llm=llm,
        prompts=prompts,
        managed_agents=[get_librarian_agent(model_name), 
                        get_mle_solver_agent(model_name),
                        # get_writer_agent(model_name),
                        get_proposer_agent(model_name)],
        tool_names=[],
        planning_interval=3,
    )

def run_main_agent(
    model_name: str = MODEL5,
    # image_paths: Sequence[str] = tuple(),
    enable_phoenix: bool = False,
    phoenix_project_name: str = "holosophos",
    phoenix_endpoint: str = "https://app.phoenix.arize.com",
) -> None:
    load_dotenv()
    if enable_phoenix and phoenix_project_name and phoenix_endpoint:
        register(
            project_name=phoenix_project_name,
            endpoint=f"{phoenix_endpoint}/v1/traces",
            auto_instrument=True,
        )
        CodeActInstrumentor().instrument()
    
    agent = compose_main_agent()
    run_server(agent, MCP_CONFIG)

if __name__ == "__main__":
    fire.Fire(run_main_agent)
