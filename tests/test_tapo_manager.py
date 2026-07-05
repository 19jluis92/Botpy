import os
from bot.system.tapo_manager import TapoManager


class FakeDetector:
    def capture_zone(self):
        return None

    def reset(self):
        return None


def test_tapo_manager_load_is_skipped_on_init(monkeypatch):
    monkeypatch.setattr(TapoManager, "load", lambda self, path: None)
    manager = TapoManager()

    assert manager.detectors == []
    assert manager.notifications_enabled is True


def test_tapo_manager_capture_zone_returns_none_when_no_frame(monkeypatch):
    monkeypatch.setattr(TapoManager, "load", lambda self, path: None)
    manager = TapoManager()
    manager.detectors = [{
        "name": "Entrada",
        "controller": None,
        "detector": FakeDetector(),
        "enabled": True,
    }]

    assert manager.capture_zone("Entrada") is None


def test_tapo_manager_reset_calls_reset_on_detectors(monkeypatch):
    monkeypatch.setattr(TapoManager, "load", lambda self, path: None)
    manager = TapoManager()
    fake_detector = FakeDetector()
    manager.detectors = [{
        "name": "Entrada",
        "controller": None,
        "detector": fake_detector,
        "enabled": True,
    }]

    manager.reset()
    assert manager.detectors[0]["detector"] is fake_detector


def test_cleanup_folder_removes_old_file(monkeypatch, tmp_path):
    monkeypatch.setattr(TapoManager, "load", lambda self, path: None)
    manager = TapoManager()
    folder = tmp_path / "capturesEntrada"
    folder.mkdir(parents=True)

    old_file = folder / "old.jpg"
    old_file.write_text("x")
    os.utime(old_file, (0, 0))

    manager.cleanup_folder(str(folder), max_age_seconds=0)
    assert not old_file.exists()


def test_cleanup_folder_missing_folder_does_not_throw(monkeypatch):
    monkeypatch.setattr(TapoManager, "load", lambda self, path: None)
    manager = TapoManager()
    manager.cleanup_folder("nonexistent-path", max_age_seconds=0)
