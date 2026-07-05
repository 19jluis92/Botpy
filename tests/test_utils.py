import asyncio
import json
from pathlib import Path

from bot.handlers.tapo_handlers import delete_image
from bot.utils import auth, sqlite_manager


class DummyMessage:
    def __init__(self):
        self.reply = None

    async def reply_text(self, text):
        self.reply = text


class DummyUser:
    def __init__(self, username):
        self.username = username


class DummyUpdate:
    def __init__(self, username):
        self.effective_user = DummyUser(username)
        self.effective_message = DummyMessage()


async def dummy_handler(update, context):
    return "ok"


def test_load_allowed_users_from_json(tmp_path, monkeypatch):
    config_file = tmp_path / "allowed_users.json"
    config_file.write_text(json.dumps({"allowed_usernames": ["LuisVE"]}), encoding="utf-8")
    monkeypatch.setattr(auth, "CONFIG_FILE", config_file)

    assert auth.load_allowed_users() == {"LuisVE"}


def test_load_allowed_users_missing_file(monkeypatch):
    monkeypatch.setattr(auth, "CONFIG_FILE", Path("missing.json"))
    assert auth.load_allowed_users() == set()


def test_restricted_wrapper_denies_access(monkeypatch):
    monkeypatch.setattr(auth, "ALLOWED_USERNAMES", {"allowed_user"})
    update = DummyUpdate("blocked_user")
    wrapped = auth.restricted(dummy_handler)

    result = asyncio.run(wrapped(update, None))

    assert result is None
    assert update.effective_message.reply == "🚫 No tienes permiso para usar este bot."


def test_sqlite_memory_lifecycle(tmp_path, monkeypatch):
    db_path = tmp_path / "lala_memory.db"
    monkeypatch.setattr(sqlite_manager, "DB_PATH", str(db_path))

    sqlite_manager.init_db()
    sqlite_manager.save_message("user1", "user", "hola")
    sqlite_manager.save_message("user1", "assistant", "hola de vuelta")

    history = sqlite_manager.load_history("user1")
    assert history == [
        {"role": "user", "content": "hola"},
        {"role": "assistant", "content": "hola de vuelta"},
    ]

    sqlite_manager.clear_memory("user1")
    assert sqlite_manager.load_history("user1") == []


def test_delete_image_removes_file(tmp_path):
    file_path = tmp_path / "temp.jpg"
    file_path.write_text("x")

    delete_image(str(file_path))
    assert not file_path.exists()


def test_delete_image_ignores_missing_file(tmp_path):
    delete_image(str(tmp_path / "missing.jpg"))
