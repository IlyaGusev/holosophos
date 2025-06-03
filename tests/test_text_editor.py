import tempfile
import os

import pytest

from holosophos.tools import text_editor
from holosophos.files import WORKSPACE_DIR_PATH

DOCUMENT1 = """
The dominant sequence transduction models are based on complex recurrent or convolutional
neural networks in an encoder-decoder configuration. The best performing models also connect
the encoder and decoder through an attention mechanism. We propose a new simple network architecture,
the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions
entirely. Experiments on two machine translation tasks show these models to be superior in quality
while being more parallelizable and requiring significantly less time to train. Our model achieves
28.4 BLEU on the WMT 2014 English-to-German translation task, improving over the existing best results,
including ensembles by over 2 BLEU. On the WMT 2014 English-to-French translation task, our model
establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on
eight GPUs, a small fraction of the training costs of the best models from the literature.
We show that the Transformer generalizes well to other tasks by applying it successfully to
English constituency parsing both with large and limited training data.
"""


def test_text_editor_view() -> None:
    with tempfile.NamedTemporaryFile(dir=WORKSPACE_DIR_PATH, mode="w+") as f:
        f.write(DOCUMENT1)
        f.flush()
        name = os.path.basename(f.name)
        test_file = WORKSPACE_DIR_PATH / name

        result = text_editor("view", name, show_lines=True)
        cmd_result = os.popen(f"cat -n {str(test_file.resolve())}").read()
        assert result.strip().startswith("1")
        assert result.strip() == cmd_result.strip()

        result = text_editor("view", name)
        cmd_result = os.popen(f"cat {str(test_file.resolve())}").read()
        assert result.strip() == cmd_result.strip()

        result = text_editor("view", name, view_start_line=1, view_end_line=5, show_lines=True)
        cmd_result = os.popen(f"head -n 5 {str(test_file.resolve())} | cat -n").read()
        assert result.strip().startswith("1")
        assert result.strip() == cmd_result.strip()

        result = text_editor("view", name, view_start_line=5, show_lines=True)
        assert result.strip().startswith("5")

        result = text_editor("view", name, view_start_line=5, view_end_line=6, show_lines=True)
        assert result.strip().startswith("5")
        assert result.splitlines()[-1].strip().startswith("6")


def test_text_editor_write() -> None:
    with tempfile.NamedTemporaryFile(dir=WORKSPACE_DIR_PATH, mode="w+") as f:
        name = os.path.basename(f.name)
        test_file = WORKSPACE_DIR_PATH / name
        test_file.unlink(missing_ok=True)
        assert not test_file.exists()

        text_editor("write", name, file_text=DOCUMENT1)
        assert test_file.exists()
        assert DOCUMENT1.strip() == test_file.open().read().strip()


def test_text_editor_insert() -> None:
    with tempfile.NamedTemporaryFile(dir=WORKSPACE_DIR_PATH, mode="w+") as f:
        name = os.path.basename(f.name)
        test_file = WORKSPACE_DIR_PATH / name
        test_file.write_text(DOCUMENT1)

        text_editor("insert", name, insert_line=0, new_str="Hello there!")
        assert test_file.open().readlines()[0].startswith("Hello there!")

        text_editor("insert", name, insert_line=5, new_str="Hello there!")
        assert test_file.open().readlines()[5].startswith("Hello there!")


def test_text_editor_str_replace() -> None:
    with tempfile.NamedTemporaryFile(dir=WORKSPACE_DIR_PATH, mode="w+") as f:
        name = os.path.basename(f.name)
        test_file = WORKSPACE_DIR_PATH / name
        test_file.write_text(DOCUMENT1)

        text_editor("str_replace", name, old_str="41.8", new_str="41.9")
        new_content = test_file.open().read()
        assert "41.9" in new_content and "41.8" not in new_content


def test_text_editor_undo_edit() -> None:
    with tempfile.NamedTemporaryFile(dir=WORKSPACE_DIR_PATH, mode="w+") as f:
        name = os.path.basename(f.name)
        test_file = WORKSPACE_DIR_PATH / name
        test_file.write_text(DOCUMENT1)

        text_editor("str_replace", name, old_str="41.8", new_str="41.9")
        new_content = test_file.open().read()
        assert "41.9" in new_content and "41.8" not in new_content

        text_editor("undo_edit", name)
        content = test_file.open().read()
        assert "41.8" in content and "41.9" not in content


def test_text_editor_view_nonexistent_file() -> None:
    with pytest.raises(AssertionError):
        text_editor("view", "nonexistent.txt")


def test_text_editor_view_directory() -> None:
    result = text_editor("view", ".")
    assert isinstance(result, str)
    assert len(result) >= 0


def test_text_editor_view_invalid_range() -> None:
    with tempfile.NamedTemporaryFile(dir=WORKSPACE_DIR_PATH, mode="w+") as f:
        name = os.path.basename(f.name)
        test_file = WORKSPACE_DIR_PATH / name
        test_file.write_text(DOCUMENT1)

        with pytest.raises(AssertionError):
            text_editor("view", name, view_start_line=-1)

        with pytest.raises(AssertionError):
            text_editor("view", name, view_start_line=10, view_end_line=5)


def test_text_editor_write_existing_file() -> None:
    with tempfile.NamedTemporaryFile(dir=WORKSPACE_DIR_PATH, mode="w+") as f:
        name = os.path.basename(f.name)
        test_file = WORKSPACE_DIR_PATH / name
        test_file.write_text(DOCUMENT1)
        text_editor("write", name, file_text="New content")


def test_text_editor_missing_required_params() -> None:
    with tempfile.NamedTemporaryFile(dir=WORKSPACE_DIR_PATH, mode="w+") as f:
        name = os.path.basename(f.name)
        test_file = WORKSPACE_DIR_PATH / name
        test_file.write_text(DOCUMENT1)

        with pytest.raises(AssertionError):
            text_editor("write", name)

        with pytest.raises(AssertionError):
            text_editor("insert", name, insert_line=0)

        with pytest.raises(AssertionError):
            text_editor("str_replace", name, new_str="New")


def test_text_editor_undo_multiple() -> None:
    with tempfile.NamedTemporaryFile(dir=WORKSPACE_DIR_PATH, mode="w+") as f:
        name = os.path.basename(f.name)
        test_file = WORKSPACE_DIR_PATH / name
        test_file.write_text(DOCUMENT1)

        text_editor("str_replace", name, old_str="41.8", new_str="41.9")
        text_editor("insert", name, insert_line=0, new_str="New line")
        text_editor("undo_edit", name)
        text_editor("undo_edit", name)

        assert test_file.read_text().strip() == DOCUMENT1.strip()

        with pytest.raises(AssertionError):
            text_editor("undo_edit", name)


def test_text_editor_str_replace_no_match() -> None:
    with tempfile.NamedTemporaryFile(dir=WORKSPACE_DIR_PATH, mode="w+") as f:
        name = os.path.basename(f.name)
        test_file = WORKSPACE_DIR_PATH / name
        test_file.write_text(DOCUMENT1)

        with pytest.raises(AssertionError):
            text_editor("str_replace", name, old_str="NonexistentText", new_str="New")


def test_text_editor_str_replace_multiple_matches() -> None:
    with tempfile.NamedTemporaryFile(dir=WORKSPACE_DIR_PATH, mode="w+") as f:
        name = os.path.basename(f.name)
        test_file = WORKSPACE_DIR_PATH / name
        test_file.write_text("Hello\nHello\nHello")

        with pytest.raises(AssertionError):
            text_editor("str_replace", name, old_str="Hello", new_str="Hi")


def test_text_editor_large_file_handling() -> None:
    with tempfile.NamedTemporaryFile(dir=WORKSPACE_DIR_PATH, mode="w+") as f:
        name = os.path.basename(f.name)
        test_file = WORKSPACE_DIR_PATH / name

        large_content = ""
        for i in range(1000):
            large_content += f"This is line {i} with some additional content to make it longer\n"
        test_file.write_text(large_content)

        result = text_editor("view", name)
        assert "This content has been truncated" in result
        assert len(result) <= 3100

        result = text_editor("view", name, view_end_line=5)
        assert "<response clipped>" not in result
        assert len(result.splitlines()) == 5


def test_text_editor_append() -> None:
    with tempfile.NamedTemporaryFile(dir=WORKSPACE_DIR_PATH, mode="w+") as f:
        name = os.path.basename(f.name)
        test_file = WORKSPACE_DIR_PATH / name
        test_file.write_text(DOCUMENT1)

        text_editor("append", name, new_str="New line")

        assert DOCUMENT1.strip() in test_file.read_text().strip()
        assert "New line" in test_file.read_text().strip()
