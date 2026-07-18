import importlib

import pytest

import core.config as config


def test_database_url_uses_postgres_environment_when_available(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("POSTGRES_HOST", "db")
    monkeypatch.setenv("POSTGRES_PORT", "5432")
    monkeypatch.setenv("POSTGRES_USER", "appuser")
    monkeypatch.setenv("POSTGRES_PASSWORD", "secret")
    monkeypatch.setenv("POSTGRES_DB", "lore")

    reloaded_config = importlib.reload(config)

    assert reloaded_config.DATABASE_URL == (
        "postgresql+psycopg://appuser:secret@db:5432/lore"
    )


def test_database_url_requires_runtime_value_in_production(monkeypatch):
    monkeypatch.setenv("RAILWAY_PROJECT_ID", "proj_test")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("POSTGRES_HOST", raising=False)
    monkeypatch.delenv("POSTGRES_PORT", raising=False)
    monkeypatch.delenv("POSTGRES_USER", raising=False)
    monkeypatch.delenv("POSTGRES_PASSWORD", raising=False)
    monkeypatch.delenv("POSTGRES_DB", raising=False)

    with pytest.raises(RuntimeError, match="DATABASE_URL must be set"):
        importlib.reload(config)


def test_database_url_uses_runtime_value_in_production(monkeypatch):
    monkeypatch.setenv("RAILWAY_PROJECT_ID", "proj_test")
    monkeypatch.setenv("DATABASE_URL", "postgresql://dbuser:dbpass@railway-host:5432/lore")

    reloaded_config = importlib.reload(config)

    assert reloaded_config.DATABASE_URL == (
        "postgresql+psycopg://dbuser:dbpass@railway-host:5432/lore"
    )


def test_database_url_rejects_localhost_in_production(monkeypatch):
    monkeypatch.setenv("RAILWAY_PROJECT_ID", "proj_test")
    monkeypatch.setenv("DATABASE_URL", "postgresql://dbuser:dbpass@localhost:5432/lore")

    with pytest.raises(RuntimeError, match="cannot target localhost"):
        importlib.reload(config)
