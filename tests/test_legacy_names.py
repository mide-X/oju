"""Backward compatibility with the pre-rename (Odysseus) names."""

from email.message import EmailMessage
from types import SimpleNamespace

from src.legacy_names import apply_legacy_env, get_header, get_or_migrate_collection


def test_legacy_env_fills_missing_new_names():
    env = {"ODYSSEUS_ADMIN_USER": "old", "ODYSSEUS_PORT": "7001", "OJU_PORT": "7002"}
    apply_legacy_env(env)
    assert env["OJU_ADMIN_USER"] == "old"
    # The new name wins when both are set.
    assert env["OJU_PORT"] == "7002"


def test_get_header_prefers_new_and_falls_back_to_legacy():
    old = EmailMessage()
    old["X-Odysseus-Kind"] = "reminder"
    assert get_header(old, "X-Oju-Kind") == "reminder"

    both = EmailMessage()
    both["X-Oju-Kind"] = "task"
    both["X-Odysseus-Kind"] = "reminder"
    assert get_header(both, "X-Oju-Kind") == "task"

    assert get_header(EmailMessage(), "X-Oju-Kind", "") == ""


class _FakeCollection:
    def __init__(self, client, name):
        self.client, self.name = client, name

    def modify(self, name):
        self.client.cols[name] = self.client.cols.pop(self.name)
        self.name = name


class _FakeChroma:
    def __init__(self, *names):
        self.cols = {n: [n] for n in names}

    def list_collections(self):
        return [SimpleNamespace(name=n) for n in self.cols]

    def get_collection(self, name):
        return _FakeCollection(self, name)

    def get_or_create_collection(self, name, **kwargs):
        self.cols.setdefault(name, [])
        return self.cols[name]


def test_collection_migrates_legacy_data():
    client = _FakeChroma("odysseus_memories")
    col = get_or_migrate_collection(client, "oju_memories", "odysseus_memories")
    assert col == ["odysseus_memories"]  # the old collection's contents
    assert set(client.cols) == {"oju_memories"}


def test_collection_leaves_legacy_alone_when_new_exists():
    client = _FakeChroma("odysseus_memories", "oju_memories")
    col = get_or_migrate_collection(client, "oju_memories", "odysseus_memories")
    assert col == ["oju_memories"]
    assert set(client.cols) == {"odysseus_memories", "oju_memories"}


def test_session_token_accepts_legacy_cookie():
    from routes.auth_routes import session_token

    assert session_token(SimpleNamespace(cookies={"odysseus_session": "old"})) == "old"
    assert session_token(SimpleNamespace(cookies={"oju_session": "new", "odysseus_session": "old"})) == "new"
    assert session_token(SimpleNamespace(cookies={})) is None
