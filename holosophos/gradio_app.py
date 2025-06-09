from dotenv import load_dotenv
import fire  # type: ignore
from smolagents import GradioUI  # type: ignore

from holosophos.main_agent import compose_main_agent


def launch_gradio(
    model_name: str = "openrouter/deepseek/deepseek-chat-v3-0324",
    port: int = 7860,
    max_print_outputs_length: int = 10_000,
    verbosity_level: int = 2,
    planning_interval: int = 3,
    max_steps: int = 30,
    file_upload_folder: str = "./data",
) -> None:
    """
    Run Gradio-demo with compose_main_agent
    """
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
        server_name="127.0.0.1",
    )


if __name__ == "__main__":
    fire.Fire(launch_gradio)
