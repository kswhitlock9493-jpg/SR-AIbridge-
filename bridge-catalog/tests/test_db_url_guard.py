#!/usr/bin/env python3
"""
Tests for db_url_guard.py
Validates URL normalization and error handling
"""
import os
import sys
import pytest
from pathlib import Path

# Add bridge_backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge_backend"))

from runtime.db_url_guard import normalize


class TestDBURLGuard:
    """Test database URL guard and normalization"""

    def test_postgres_to_asyncpg(self):
        """Test postgres:// gets converted to postgresql+asyncpg://"""
        url = "postgres://user:pass@host:5432/dbname"
        result = normalize(url)
        assert result.startswith("postgresql+asyncpg://")
        assert "user:pass@host:5432/dbname" in result

    def test_postgresql_to_asyncpg(self):
        """Test postgresql:// gets converted to postgresql+asyncpg://"""
        url = "postgresql://user:pass@host:5432/dbname"
        result = normalize(url)
        assert result.startswith("postgresql+asyncpg://")
        assert "user:pass@host:5432/dbname" in result

    def test_asyncpg_preserved(self):
        """Test postgresql+asyncpg:// is preserved"""
        url = "postgresql+asyncpg://user:pass@host:5432/dbname"
        result = normalize(url)
        assert result == url

    def test_sqlite_url(self):
        """Test SQLite URL passes through"""
        url = "sqlite+aiosqlite:///./bridge_local.db"
        result = normalize(url)
        assert result == url

    def test_empty_url_with_fallback(self, monkeypatch):
        """Test empty URL with SQLite fallback enabled"""
        monkeypatch.setenv("DB_FALLBACK_TO_SQLITE", "true")
        result = normalize("")
        assert result == "sqlite+aiosqlite:///./bridge_local.db"

    def test_empty_url_without_fallback(self, monkeypatch):
        """Test empty URL without fallback exits with code 12"""
        monkeypatch.setenv("DB_FALLBACK_TO_SQLITE", "false")
        with pytest.raises(SystemExit) as excinfo:
            normalize("")
        assert excinfo.value.code == 12

    def test_malformed_url_percent_40(self):
        """Test URL with %40 glued to host exits with code 13"""
        url = "postgresql://user:pass%40host:5432/dbname"
        with pytest.raises(SystemExit) as excinfo:
            normalize(url)
        assert excinfo.value.code == 13

    def test_malformed_url_no_scheme(self):
        """Test URL without scheme exits with code 14"""
        url = "user:pass@host:5432/dbname"
        with pytest.raises(SystemExit) as excinfo:
            normalize(url)
        assert excinfo.value.code == 14

    def test_malformed_url_no_netloc(self):
        """Test URL without netloc exits with code 14"""
        url = "postgresql://"
        with pytest.raises(SystemExit) as excinfo:
            normalize(url)
        assert excinfo.value.code == 14

    def test_postgresql_missing_at(self):
        """Test PostgreSQL URL missing @ exits with code 15"""
        url = "postgresql://userpasshost:5432/dbname"
        with pytest.raises(SystemExit) as excinfo:
            normalize(url)
        assert excinfo.value.code == 15

    def test_postgresql_missing_port(self):
        """Test PostgreSQL URL missing port exits with code 15"""
        url = "postgresql://user:pass@host/dbname"
        with pytest.raises(SystemExit) as excinfo:
            normalize(url)
        assert excinfo.value.code == 15

    def test_valid_postgresql_url(self):
        """Test valid PostgreSQL URL normalizes correctly"""
        url = "postgresql://sr_bridge_user:SRsecure@render-db:5432/sr_aibridge_main"
        result = normalize(url)
        assert result == "postgresql+asyncpg://sr_bridge_user:SRsecure@render-db:5432/sr_aibridge_main"

    def test_complex_password(self):
        """Test URL with special characters in password"""
        url = "postgresql://user:p@ss!w0rd@host:5432/db"
        result = normalize(url)
        assert result == "postgresql+asyncpg://user:p@ss!w0rd@host:5432/db"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
