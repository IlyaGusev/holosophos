from dotenv import load_dotenv
import fire  # type: ignore
from smolagents import GradioUI  # type: ignore

from holosophos.main_agent import compose_main_agent
from holosophos.files import WORKSPACE_DIR_PATH


def launch_gradio(
    model_name: str = "openrouter/deepseek/deepseek-chat-v3-0324",
    port: int = 7860,
    host: str = "127.0.0.1",
    share: bool = False,
    max_print_outputs_length: int = 10_000,
    verbosity_level: int = 2,
    planning_interval: int = 3,
    max_steps: int = 30,
    file_upload_folder: str = str(WORKSPACE_DIR_PATH),
) -> None:
    load_dotenv()

    agent = compose_main_agent(
        model_name=model_name,
        max_print_outputs_length=max_print_outputs_length,
        verbosity_level=verbosity_level,
        planning_interval=planning_interval,
        max_steps=max_steps,
        stream_outputs=True,
    )

    GradioUI(agent, file_upload_folder=file_upload_folder).launch(
        server_port=port,
        server_name=host,
        share=share,
    )


if __name__ == "__main__":
    fire.Fire(launch_gradio)
