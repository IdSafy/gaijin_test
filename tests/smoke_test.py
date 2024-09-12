import pytest
from click.testing import CliRunner

from gaijin_test import main


@pytest.fixture
def test_dir_1() -> str:
    return "tests/data/test_dir_1"


def test_smoke_against_test_dir_1(test_dir_1: str, capfd: pytest.CaptureFixture) -> None:
    runner = CliRunner()
    result = runner.invoke(main, [test_dir_1])
    assert result.exit_code == 0
    output_lines = result.output.split("\n")

    assert "I'm the side effect! Behold!" in output_lines
    output_lines.remove("I'm the side effect! Behold!")

    error_line = None
    for line in output_lines:
        if "Error loading module; invalid syntax" in line:
            error_line = line
            break
    assert error_line is not None
    output_lines.remove(error_line)

    assert "Command `echo 2` already executed." in output_lines
    output_lines.remove("Command `echo 2` already executed.")

    assert len(output_lines) == 1  # empty string
    assert output_lines[0] == ""

    assert capfd.readouterr().out == "4\n5\n2\n3\n1\n"
