import os
import time
import subprocess
import atexit
import signal
import inspect
import functools
from pathlib import Path
from typing import List, Optional, Any, Callable
from dataclasses import dataclass

from dotenv import load_dotenv
from vastai_sdk import VastAI  # type: ignore

from holosophos.files import WORKSPACE_DIR_PATH

BASE_IMAGE = "phoenix120/holosophos_mle"
DEFAULT_GPU_TYPE = "RTX_3090"
GLOBAL_TIMEOUT = 43200
VAST_AI_GREETING = """Welcome to vast.ai. If authentication fails, try again after a few seconds, and double check your ssh key.
Have fun!"""


@dataclass
class InstanceInfo:
    instance_id: int
    ip: str = ""
    port: int = 0
    username: str = ""
    ssh_key_path: str = ""
    gpu_name: str = ""
    start_time: int = 0


_sdk: Optional[VastAI] = None
_instance_info: Optional[InstanceInfo] = None


def cleanup_machine(signum: Optional[Any] = None, frame: Optional[Any] = None) -> None:
    print("Cleaning up...")
    global _instance_info
    signal.alarm(0)
    if _instance_info and _sdk:
        try:
            _sdk.destroy_instance(id=_instance_info.instance_id)
            _instance_info = None
        except Exception:
            pass
    if signum == signal.SIGINT:
        raise KeyboardInterrupt()


atexit.register(cleanup_machine)
signal.signal(signal.SIGINT, cleanup_machine)
signal.signal(signal.SIGTERM, cleanup_machine)
signal.signal(signal.SIGALRM, cleanup_machine)


def wait_for_instance(vast_sdk: VastAI, instance_id: str, max_wait_time: int = 300) -> bool:
    print(f"Waiting for instance {instance_id} to be ready...")
    start_wait = int(time.time())
    instance_ready = False
    while time.time() - start_wait < max_wait_time:
        instance_details = vast_sdk.show_instance(id=instance_id)
        if (
            isinstance(instance_details, dict)
            and instance_details.get("actual_status") == "running"
        ):
            instance_ready = True
            print(f"Instance {instance_id} is running and ready.")
            break
        print(f"Instance {instance_id} not ready yet. Waiting...")
        time.sleep(15)
    return instance_ready


def get_offers(vast_sdk: VastAI, gpu_name: str) -> List[int]:
    params = [
        f"gpu_name={gpu_name}",
        "cuda_vers>=12.1",
        "num_gpus=1",
        "reliability > 0.99",
        "inet_up > 400",
        "inet_down > 400",
        "verified=True",
        "rentable=True",
        "disk_space > 100",
    ]
    query = "  ".join(params)
    order = "score-"
    offers = vast_sdk.search_offers(query=query, order=order)
    assert offers
    return [int(o["id"]) for o in offers]


def run_command(
    instance: InstanceInfo, command: str, timeout: int = 60
) -> subprocess.CompletedProcess[str]:
    cmd = [
        "ssh",
        "-i",
        instance.ssh_key_path,
        "-p",
        str(instance.port),
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "ConnectTimeout=10",
        "-o",
        "ServerAliveInterval=30",
        "-o",
        "ServerAliveCountMax=3",
        "-o",
        "TCPKeepAlive=yes",
        f"{instance.username}@{instance.ip}",
        command,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            raise Exception(
                f"Error running command: {command}; "
                f"Output: {result.stdout}; "
                f"Error: {result.stderr}"
            )
    except subprocess.TimeoutExpired:
        raise Exception(
            f"Command timed out after {timeout} seconds: {command}; "
            f"Host: {instance.username}@{instance.ip}:{instance.port}"
        )
    return result


def recieve_rsync(
    info: InstanceInfo, remote_path: str, local_path: str
) -> subprocess.CompletedProcess[str]:
    rsync_cmd = [
        "rsync",
        "-avz",
        "-e",
        f"ssh -i {info.ssh_key_path} -p {info.port} -o StrictHostKeyChecking=no",
        f"{info.username}@{info.ip}:{remote_path}",
        local_path,
    ]

    result = subprocess.run(rsync_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        error_output = (
            f"Error syncing directory: {remote_path} to {local_path}. Error: {result.stderr}"
        )
        raise Exception(error_output)
    return result


def send_rsync(
    info: InstanceInfo, local_path: str, remote_path: str
) -> subprocess.CompletedProcess[str]:
    rsync_cmd = [
        "rsync",
        "-avz",
        "-e",
        f"ssh -i {info.ssh_key_path} -p {info.port} -o StrictHostKeyChecking=no",
        local_path,
        f"{info.username}@{info.ip}:{remote_path}",
    ]

    result = subprocess.run(rsync_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        error_output = (
            f"Error syncing directory: {local_path} to {remote_path}. Error: {result.stderr}"
        )
        raise Exception(error_output)
    return result


def launch_instance(vast_sdk: VastAI, gpu_name: str) -> Optional[InstanceInfo]:
    print(f"Selecting instance with {gpu_name}...")
    offer_ids = get_offers(vast_sdk, gpu_name)

    instance_id = None
    for offer_id in offer_ids:
        print(f"Launching offer {offer_id}...")
        instance = vast_sdk.create_instance(id=offer_id, image=BASE_IMAGE, disk=50.0)
        if not instance["success"]:
            continue
        instance_id = instance["new_contract"]
        assert instance_id
        global _instance_info
        _instance_info = InstanceInfo(instance_id=instance_id)
        print(f"Instance launched successfully. ID: {instance_id}")
        is_ready = wait_for_instance(vast_sdk, instance_id)
        if not is_ready:
            print(f"Destroying instance {instance_id}...")
            vast_sdk.destroy_instance(id=instance_id)
            continue

        print("Attaching SSH key...")
        ssh_key_path = Path("~/.ssh/id_rsa").expanduser()
        if not ssh_key_path.exists():
            print(f"Generating SSH key at {ssh_key_path}...")
            os.makedirs(ssh_key_path.parent, exist_ok=True)
            subprocess.run(
                [
                    "ssh-keygen",
                    "-t",
                    "rsa",
                    "-b",
                    "4096",
                    "-f",
                    str(ssh_key_path),
                    "-N",
                    "",
                ]
            )

        public_key = Path(f"{ssh_key_path}.pub").read_text().strip()
        vast_sdk.attach_ssh(instance_id=instance_id, ssh_key=public_key)
        instance_details = vast_sdk.show_instance(id=instance_id)

        info = InstanceInfo(
            instance_id=instance_details.get("id"),
            ip=instance_details.get("ssh_host"),
            port=instance_details.get("ssh_port"),
            username="root",
            ssh_key_path=str(ssh_key_path),
            gpu_name=instance_details.get("gpu_name"),
            start_time=int(time.time()),
        )

        print(info)
        print(f"Checking SSH connection to {info.ip}:{info.port}...")
        max_attempts = 10
        is_okay = False
        for attempt in range(max_attempts):
            try:
                result = run_command(info, "echo 'SSH connection successful'")
            except Exception as e:
                print(f"Waiting for SSH... {e}\n(Attempt {attempt+1}/{max_attempts})")
                time.sleep(30)
                continue
            if "SSH connection successful" in result.stdout:
                print("SSH connection established successfully!")
                is_okay = True
                break
            print(f"Waiting for SSH... (Attempt {attempt+1}/{max_attempts})")
            time.sleep(30)

        if not is_okay:
            print(f"Destroying instance {instance_id}...")
            vast_sdk.destroy_instance(id=instance_id)
            continue

        break

    return info


def send_scripts() -> None:
    assert _instance_info
    for name in os.listdir(WORKSPACE_DIR_PATH):
        if name.endswith(".py"):
            send_rsync(_instance_info, f"{WORKSPACE_DIR_PATH}/{name}", "/root")


def init_all() -> None:
    global _sdk, _instance_info

    load_dotenv()

    if not _sdk:
        _sdk = VastAI(api_key=os.getenv("VAST_AI_KEY"))
    assert _sdk

    signal.alarm(GLOBAL_TIMEOUT)
    if not _instance_info:
        _instance_info = launch_instance(_sdk, DEFAULT_GPU_TYPE)

    if _instance_info:
        send_scripts()

    assert _instance_info, "Failed to connect to a remote instance! Try again"


def remote_bash(command: str, timeout: Optional[int] = 60) -> str:
    """
    Run commands in a bash shell on a remote machine with GPU cards.
    When invoking this tool, the contents of the "command" parameter does NOT need to be XML-escaped.
    You don't have access to the internet via this tool.
    You do have access to a mirror of common linux and python packages via apt and pip.
    State is persistent across command calls and discussions with the user.
    To inspect a particular line range of a file, e.g. lines 10-25, try 'sed -n 10,25p /path/to/the/file'.
    Please avoid commands that may produce a very large amount of output.
    Do not run commands in the background.
    You can use python3.

    Args:
        command: The bash command to run.
        timeout: Timeout for the command execution. 60 seconds by default. Set a higher value for heavy jobs.
    """

    init_all()
    assert _instance_info
    assert timeout
    result = run_command(_instance_info, command, timeout=timeout)
    output = ("STDOUT: " + result.stdout + "\n") if result.stdout else ""
    output += ("STDERR: " + result.stderr) if result.stderr else ""
    return output.replace(VAST_AI_GREETING, "")


def remote_download(file_path: str) -> str:
    """
    Copies a file from a remote machine to the local work directory.
    Use it to download final artefacts of the runs.
    Args:
        file_path: Path to the file on a remote machine.
    """
    init_all()
    assert _instance_info
    recieve_rsync(_instance_info, f"/root/{file_path}", f"{WORKSPACE_DIR_PATH}")
    return f"File '{file_path}' downloaded!"


def create_remote_text_editor(
    text_editor_func: Callable[..., str],
) -> Callable[..., str]:
    @functools.wraps(text_editor_func)
    def wrapper(*args: Any, **kwargs: Any) -> str:
        init_all()
        assert _instance_info

        args_dict = {k: v for k, v in kwargs.items()}
        if args:
            args_dict.update(dict(zip(("command", "path"), args)))
        path = args_dict["path"]
        command = args_dict["command"]

        if command != "write":
            recieve_rsync(_instance_info, f"/root/{path}", f"{WORKSPACE_DIR_PATH}")

        result: str = text_editor_func(*args, **kwargs)

        if command != "view":
            send_rsync(_instance_info, f"{WORKSPACE_DIR_PATH}/{path}", "/root")

        return result

    orig_sig = inspect.signature(text_editor_func)
    wrapper.__signature__ = orig_sig  # type: ignore
    if text_editor_func.__doc__:
        orig_doc = text_editor_func.__doc__
        new_doc = orig_doc.replace("text_editor", "remote_text_editor")
        wrapper.__doc__ = "Executes on a remote machine with GPU.\n" + new_doc
        wrapper.__name__ = "remote_text_editor"
    return wrapper
