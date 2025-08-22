import os
import logging
from typing import Any, Optional

import fire  # type: ignore
from phoenix.otel import register
from dotenv import load_dotenv
from codearkt.codeact import CodeActAgent, Prompts
from codearkt.llm import LLM
from codearkt.otel import CodeActInstrumentor
from codearkt.server import run_query

from holosophos.files import PROMPTS_DIR_PATH

from holosophos.agents import (
    get_librarian_agent,
    get_mle_solver_agent,
    get_writer_agent,
    get_proposer_agent,
)


PROMPT1 = """
What is the best model for Russian in a role-play benchmark by Ilya Gusev?
What final scores does it have?
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
Compose a comprehensive PDF report and save into "report.pdf"
"""


MODEL1 = "deepseek/deepseek-chat-v3-0324"

EXA_API_KEY = os.getenv("EXA_API_KEY", "")
MCP_CONFIG = {
    "mcpServers": {
        "academia": {"url": "http://0.0.0.0:5056/mcp", "transport": "streamable-http"},
        "mle_kit": {"url": "http://0.0.0.0:5057/mcp", "transport": "streamable-http"},
    }
}


def compose_main_agent(
    model_name: str = MODEL1,
    verbosity_level: int = logging.INFO,
    planning_interval: Optional[int] = None,
    max_iterations: int = 30,
    librarian_max_iterations: int = 42,
    mle_solver_max_iterations: int = 42,
    writer_max_iterations: int = 42,
    proposer_max_iterations: int = 10,
    librarian_planning_interval: Optional[int] = 4,
    mle_solver_planning_interval: Optional[int] = 7,
    writer_planning_interval: Optional[int] = None,
    proposer_planning_interval: Optional[int] = 4,
) -> CodeActAgent:
    load_dotenv()
    model = LLM(model_name=model_name, max_completion_tokens=8192)

    librarian_agent = get_librarian_agent(
        model=model,
        verbosity_level=verbosity_level,
        max_iterations=librarian_max_iterations,
        planning_interval=librarian_planning_interval,
    )
    mle_solver_agent = get_mle_solver_agent(
        model=model,
        max_iterations=mle_solver_max_iterations,
        verbosity_level=verbosity_level,
        planning_interval=mle_solver_planning_interval,
    )
    writer_agent = get_writer_agent(
        model=model,
        max_iterations=writer_max_iterations,
        verbosity_level=verbosity_level,
        planning_interval=writer_planning_interval,
    )
    proposer_agent = get_proposer_agent(
        model=model,
        max_iterations=proposer_max_iterations,
        verbosity_level=verbosity_level,
        planning_interval=proposer_planning_interval,
    )
    prompts = Prompts.load(PROMPTS_DIR_PATH / "system.yaml")
    agent = CodeActAgent(
        name="manager",
        description="Manager agent",
        tool_names=[],
        managed_agents=[
            librarian_agent,
            mle_solver_agent,
            writer_agent,
            proposer_agent,
        ],
        llm=model,
        max_iterations=max_iterations,
        planning_interval=planning_interval,
        verbosity_level=verbosity_level,
        prompts=prompts,
    )
    return agent


async def run_main_agent(
    query: str = PROMPT4,
    model_name: str = MODEL1,
    verbosity_level: int = logging.DEBUG,
    planning_interval: int = 3,
    max_iterations: int = 30,
    enable_phoenix: bool = False,
    phoenix_project_name: str = "holosophos",
    phoenix_endpoint: str = "http://localhost:6006/v1/traces",
) -> Any:
    load_dotenv()
    if enable_phoenix and phoenix_project_name and phoenix_endpoint:
        register(
            project_name=phoenix_project_name,
            endpoint=phoenix_endpoint,
            auto_instrument=True,
        )
        CodeActInstrumentor().instrument()
    agent = compose_main_agent(
        model_name=model_name,
        verbosity_level=verbosity_level,
        planning_interval=planning_interval,
        max_iterations=max_iterations,
    )
    return await run_query(query, agent, mcp_config=MCP_CONFIG)


if __name__ == "__main__":
    fire.Fire(run_main_agent)
