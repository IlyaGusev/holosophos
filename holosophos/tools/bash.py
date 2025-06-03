import docker  # type: ignore
import atexit
import signal
from typing import Optional, Any

from holosophos.files import WORKSPACE_DIR_PATH


_container = None
_client = None

BASE_IMAGE = "python:3.9-slim"
DOCKER_WORKSPACE_DIR_PATH = "/workdir"


def cleanup_container(signum: Optional[Any] = None, frame: Optional[Any] = None) -> None:
    global _container
    if _container:
        try:
            _container.remove(force=True)
            _container = None
        except Exception:
            pass
    if signum == signal.SIGINT:
        raise KeyboardInterrupt()


atexit.register(cleanup_container)
signal.signal(signal.SIGINT, cleanup_container)
signal.signal(signal.SIGTERM, cleanup_container)


def bash(command: str) -> str:
    """
    Run commands in a bash shell.
    When invoking this tool, the contents of the "command" parameter does NOT need to be XML-escaped.
    You don't have access to the internet via this tool.
    You do have access to a mirror of common linux and python packages via apt and pip.
    State is persistent across command calls and discussions with the user.
    To inspect a particular line range of a file, e.g. lines 10-25, try 'sed -n 10,25p /path/to/the/file'.
    Please avoid commands that may produce a very large amount of output.
    Please run long lived commands in the background, e.g. 'sleep 10 &' or start a server in the background.

    Args:
        command: The bash command to run.
    """

    global _container, _client

    if not _client:
        _client = docker.from_env()

    if not _container:
        try:
            _container = _client.containers.get("bash_runner")
        except docker.errors.NotFound:
            _container = _client.containers.run(
                BASE_IMAGE,
                "tail -f /dev/null",
                detach=True,
                remove=True,
                name="bash_runner",
                tty=True,
                stdin_open=True,
                volumes={
                    WORKSPACE_DIR_PATH: {
                        "bind": DOCKER_WORKSPACE_DIR_PATH,
                        "mode": "rw",
                    }
                },
                working_dir=DOCKER_WORKSPACE_DIR_PATH,
            )

    result = _container.exec_run(
        ["bash", "-c", command],
        workdir=DOCKER_WORKSPACE_DIR_PATH,
        stdout=True,
        stderr=True,
    )
    output: str = result.output.decode("utf-8").strip()
    return output
