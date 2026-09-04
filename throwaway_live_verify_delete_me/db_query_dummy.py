"""Throwaway fixture file — not real code, see ../README.md."""

import sqlite3


def dummy_find_user(conn: sqlite3.Connection, username: str):
    """SQL built via f-string interpolation — classic injection shape,
    intentionally left unparameterized in this disposable fixture."""
    query = f"SELECT id, email FROM users WHERE username = '{username}'"
    cursor = conn.execute(query)
    return cursor.fetchone()


def dummy_delete_order(conn: sqlite3.Connection, order_id: str):
    query = "DELETE FROM orders WHERE id = " + order_id
    conn.execute(query)
    conn.commit()
