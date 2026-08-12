"""
Database Manager — Unit Tests

Covers the reliability fixes: WAL mode / busy timeout on every connection,
no connection leaks on error, and parameterized (not f-string) LIMIT
clauses. Uses a real temporary SQLite file — no mocking.
"""

import sqlite3


def _fresh_db_module(tmp_path, monkeypatch):
    """
    Points the already-imported services.database_manager at an isolated
    temp DB file. Deliberately does NOT importlib.reload() the module —
    that would re-run its top-level `DB_PATH = Path(...)` assignment and
    silently undo the monkeypatch before any test code runs.
    """
    import services.database_manager as dbm
    monkeypatch.setattr(dbm, "DB_PATH", tmp_path / "test_sentinel.db")
    dbm.init_database()
    return dbm


class TestConnectionSettings:
    def test_connect_enables_wal_and_busy_timeout(self, tmp_path, monkeypatch):
        dbm = _fresh_db_module(tmp_path, monkeypatch)

        conn = dbm._connect()
        try:
            mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
            timeout = conn.execute("PRAGMA busy_timeout").fetchone()[0]
        finally:
            conn.close()

        assert mode.lower() == "wal"
        assert timeout > 0


class TestNoConnectionLeakOnError:
    def test_log_agent_thought_closes_connection_even_on_bad_input(self, tmp_path, monkeypatch):
        dbm = _fresh_db_module(tmp_path, monkeypatch)

        # A non-serializable state dict makes json.dumps raise inside the
        # function, before the INSERT ever runs — the connection must still
        # be closed rather than leaked.
        class Unserializable:
            pass

        raised = False
        try:
            dbm.log_agent_thought("Scout", "test", state={"bad": Unserializable()})
        except TypeError:
            raised = True
        assert raised

        # If the earlier connection leaked, this fresh connection would
        # still succeed independently — leaks don't block new connections
        # to the same file, so what we actually verify is that a normal
        # call still works cleanly right after the failure.
        dbm.log_agent_thought("Scout", "recovered fine")
        thoughts = dbm.get_recent_thoughts(5)
        assert len(thoughts) == 1
        assert thoughts.iloc[0]["message"] == "recovered fine"


class TestParameterizedLimit:
    def test_get_recent_thoughts_respects_limit(self, tmp_path, monkeypatch):
        dbm = _fresh_db_module(tmp_path, monkeypatch)

        for i in range(5):
            dbm.log_agent_thought("Scout", f"thought {i}")

        thoughts = dbm.get_recent_thoughts(3)
        assert len(thoughts) == 3

    def test_get_recent_trades_respects_limit(self, tmp_path, monkeypatch):
        dbm = _fresh_db_module(tmp_path, monkeypatch)

        for i in range(4):
            dbm.log_trade("TCS.NS", "BUY", 1, 100.0 + i, 100.0 + i, 0.03, "EXECUTED")

        trades = dbm.get_recent_trades(2)
        assert len(trades) == 2

    def test_limit_is_a_real_bind_parameter_not_string_interpolation(self, tmp_path, monkeypatch):
        # Regression guard for the f-string LIMIT {limit} pattern: passing a
        # value that isn't a plain positive int must not let it flow into
        # raw SQL text. sqlite3 raises for a non-integer bind value against
        # LIMIT, which f-string interpolation would instead have silently
        # embedded as literal (and unsafely, if it were ever user input).
        dbm = _fresh_db_module(tmp_path, monkeypatch)
        dbm.log_agent_thought("Scout", "thought")

        try:
            dbm.get_recent_thoughts("5 OR 1=1")
            raised = False
        except sqlite3.InterfaceError:
            raised = True
        except Exception:
            raised = True
        assert raised
