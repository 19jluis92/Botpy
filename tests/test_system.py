import os
import subprocess
import socket
import time
import asyncio

import pytest
from bot.system.controlador_docker import DockerController
from bot.system.controlador_ngrok import NgrokController
from bot.system.controlador_roku import RokuController
from bot.system.controlador_sistema import SistemaController
from bot.system.controlador_openai import OpenAIManager
from bot.system.controlador_tapo import TapoController


class DummyPopen:
    def __init__(self, args):
        self.args = args


def test_get_system_info():
    info = SistemaController().get_system_info()
    assert set(info.keys()) >= {"OS", "Version", "Release", "Machine", "Processor"}


def test_get_usage():
    usage = SistemaController().get_usage()
    assert set(usage.keys()) == {"cpu_percent", "ram_percent", "disk_percent"}


def test_get_temperature(monkeypatch):
    monkeypatch.setattr(subprocess, "check_output", lambda cmd: b"temp=42.5'C\n")
    assert SistemaController().get_temperature() == 42.5


def test_get_ip_local(monkeypatch):
    monkeypatch.setattr(socket, "gethostname", lambda: "host1")
    monkeypatch.setattr(socket, "gethostbyname", lambda host: "127.0.0.1")
    assert SistemaController().get_ip_local() == "127.0.0.1"


def test_get_ip_public(monkeypatch):
    monkeypatch.setattr(subprocess, "check_output", lambda cmd: b"203.0.113.5\n")
    assert SistemaController().get_ip_public() == "203.0.113.5"


def test_shutdown_and_reboot(monkeypatch):
    monkeypatch.setattr(subprocess, "Popen", DummyPopen)
    controller = SistemaController()

    assert controller.shutdown() == "Apagando el sistema…"
    assert controller.reboot() == "Reiniciando el sistema…"


def test_reset_interface_success(monkeypatch):
    calls = []

    def fake_run(cmd, check=True):
        calls.append(cmd)

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(time, "sleep", lambda x: None)

    controller = SistemaController()
    assert controller.reset_interface("eth0", seconds=0) == "🔌 Interfaz eth0 reiniciada correctamente."
    assert calls == [["sudo", "ip", "link", "set", "eth0", "down"], ["sudo", "ip", "link", "set", "eth0", "up"]]


def test_restart_wifi_network_manager_fallback(monkeypatch):
    def fake_run(cmd, check=True):
        if cmd[:2] == ["sudo", "ifdown"]:
            raise subprocess.CalledProcessError(1, cmd)
        return None

    monkeypatch.setattr(subprocess, "run", fake_run)

    controller = SistemaController()
    assert "NetworkManager" in controller.restart_wifi()


def test_restart_ethernet_network_manager_fallback(monkeypatch):
    def fake_run(cmd, check=True):
        if cmd[:2] == ["sudo", "ifdown"]:
            raise subprocess.CalledProcessError(1, cmd)
        return None

    monkeypatch.setattr(subprocess, "run", fake_run)

    controller = SistemaController()
    assert "NetworkManager" in controller.restart_ethernet()


def test_docker_controller_reports_unavailable(monkeypatch):
    monkeypatch.setattr("bot.system.controlador_docker.docker.from_env", lambda: (_ for _ in ()).throw(RuntimeError("no docker")))
    controller = DockerController()

    assert controller.is_ready() is False
    assert controller.list_containers() == "❌ Docker no está disponible."
    assert "disponible" in controller.get_logs("dummy")
    assert "disponible" in controller.start_container("dummy")


def test_ngrok_requires_api_key(monkeypatch):
    monkeypatch.delenv("NGROK_API_KEY", raising=False)
    with pytest.raises(RuntimeError):
        NgrokController()


def test_ngrok_public_urls(monkeypatch):
    monkeypatch.setenv("NGROK_API_KEY", "fake-key")
    controller = NgrokController()

    class DummyResponse:
        def __init__(self, data):
            self._data = data

        def raise_for_status(self):
            pass

        def json(self):
            return self._data

    monkeypatch.setattr("bot.system.controlador_ngrok.requests.get", lambda url, headers: DummyResponse({"tunnels": [{"public_url": "https://example.ngrok.io"}]}))
    assert controller.get_public_urls() == ["https://example.ngrok.io"]


def test_roku_controller_requires_ip():
    controller = RokuController()
    with pytest.raises(RuntimeError):
        asyncio.run(controller.connect())


def test_roku_controller_set_ip():
    controller = RokuController()
    controller.set_ip("1.2.3.4")
    assert controller.ip == "1.2.3.4"


def test_openai_manager_requires_api_key():
    manager = OpenAIManager("127.0.0.1", 8000, "", "gpt-4")
    with pytest.raises(ValueError):
        asyncio.run(manager.connect())


def test_tapo_controller_save_frame(tmp_path):
    controller = TapoController("Entrada", "rtsp://test")
    output_path = controller.save_frame(b"frame", output_dir=str(tmp_path / "captures"))

    assert output_path.endswith(".jpg")
    assert "capturesEntrada" in output_path
