import importlib.util
from pathlib import Path
from types import SimpleNamespace


def _load_main_module():
    project_root = Path(__file__).resolve().parents[1]
    main_path = project_root / "main.py"

    spec = importlib.util.spec_from_file_location("lore_prototype_main", main_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


main = _load_main_module()


class FakeUserModel:
    email = "email"
    username = "username"

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class FakeDB:
    def __init__(self, first_results):
        self._first_results = iter(first_results)
        self.added = []
        self.commit_count = 0
        self.closed = False

    def query(self, _model):
        return self

    def filter(self, *_args, **_kwargs):
        return self

    def first(self):
        return next(self._first_results, None)

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        self.commit_count += 1

    def close(self):
        self.closed = True


def test_ensure_bootstrap_admin_promotes_existing_user(monkeypatch):
    existing_user = SimpleNamespace(is_admin=False)
    fake_db = FakeDB([existing_user])

    monkeypatch.setattr(main, "ENABLE_BOOTSTRAP_ADMIN", True)
    monkeypatch.setattr(main, "BOOTSTRAP_ADMIN_EMAIL", "admin@lore.app")
    monkeypatch.setattr(main, "BOOTSTRAP_ADMIN_PASSWORD", "Admin1234!")
    monkeypatch.setattr(main, "BOOTSTRAP_ADMIN_USERNAME", "lore_admin")
    monkeypatch.setattr(main, "SessionLocal", lambda: fake_db)
    monkeypatch.setattr(main, "User", FakeUserModel)

    main.ensure_bootstrap_admin()

    assert existing_user.is_admin is True
    assert fake_db.commit_count == 1
    assert fake_db.added == []
    assert fake_db.closed is True


def test_ensure_bootstrap_admin_creates_user_when_missing(monkeypatch):
    fake_db = FakeDB([
        None,
        object(),
        None,
    ])

    monkeypatch.setattr(main, "ENABLE_BOOTSTRAP_ADMIN", True)
    monkeypatch.setattr(main, "BOOTSTRAP_ADMIN_EMAIL", "admin@lore.app")
    monkeypatch.setattr(main, "BOOTSTRAP_ADMIN_PASSWORD", "Admin1234!")
    monkeypatch.setattr(main, "BOOTSTRAP_ADMIN_USERNAME", "lore_admin")
    monkeypatch.setattr(main, "SessionLocal", lambda: fake_db)
    monkeypatch.setattr(main, "User", FakeUserModel)
    monkeypatch.setattr(main, "hash_password", lambda password: f"hashed::{password}")

    main.ensure_bootstrap_admin()

    assert fake_db.commit_count == 1
    assert len(fake_db.added) == 1
    created = fake_db.added[0]
    assert created.username == "lore_admin_1"
    assert created.email == "admin@lore.app"
    assert created.hashed_password == "hashed::Admin1234!"
    assert created.is_admin is True
    assert created.is_active is True
    assert fake_db.closed is True


def test_ensure_bootstrap_admin_disabled(monkeypatch):
    monkeypatch.setattr(main, "ENABLE_BOOTSTRAP_ADMIN", False)
    monkeypatch.setattr(main, "BOOTSTRAP_ADMIN_EMAIL", "admin@lore.app")
    monkeypatch.setattr(main, "BOOTSTRAP_ADMIN_PASSWORD", "Admin1234!")

    def _session_local_should_not_run():
        raise AssertionError("SessionLocal should not be called when bootstrap is disabled")

    monkeypatch.setattr(main, "SessionLocal", _session_local_should_not_run)

    main.ensure_bootstrap_admin()
