"""Port ownership checks that turn 'another program answers on our port' into a clear error."""
import socket

import pytest

from app.core import port_guard


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        (["uvicorn", "app.main:app", "--port", "8001"], 8001),
        (["uvicorn", "app.main:app", "--port=8123"], 8123),
        (["uvicorn", "app.main:app", "--reload"], port_guard.UVICORN_DEFAULT_PORT),
    ],
)
def test_serving_port_reads_the_uvicorn_command_line(argv: list[str], expected: int, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("UVICORN_PORT", raising=False)
    assert port_guard.serving_port(argv) == expected


def test_serving_port_falls_back_to_the_launcher_environment(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("UVICORN_PORT", "8044")
    assert port_guard.serving_port(["python", "-m", "app"]) == 8044


def test_port_in_use_detects_a_listener():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        port = listener.getsockname()[1]
        assert port_guard.port_in_use(port)
    assert not port_guard.port_in_use(port)


@pytest.mark.asyncio
async def test_a_port_answered_by_another_program_is_reported(monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture):
    async def someone_else(_port: int) -> bool:
        return False

    monkeypatch.setattr(port_guard, "reaches_this_process", someone_else)
    with caplog.at_level("ERROR", logger="uvicorn.error"):
        await port_guard.warn_if_port_shadowed(8000, delay_seconds=0)
    assert "answered by another program" in caplog.text


@pytest.mark.asyncio
async def test_an_unreachable_port_is_not_misreported(monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture):
    async def unknown(_port: int) -> None:
        return None

    monkeypatch.setattr(port_guard, "reaches_this_process", unknown)
    with caplog.at_level("ERROR", logger="uvicorn.error"):
        await port_guard.warn_if_port_shadowed(8000, delay_seconds=0)
    assert caplog.text == ""
