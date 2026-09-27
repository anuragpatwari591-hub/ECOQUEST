"""Thin wrapper around PyMySQL for connection handling and simple queries."""
import pymysql
import pymysql.cursors
from flask import current_app, g


def get_db():
    """Return a request-scoped MySQL connection, creating it if needed."""
    if "db" not in g:
        cfg = current_app.config
        g.db = pymysql.connect(
            host=cfg["DB_HOST"],
            port=cfg["DB_PORT"],
            user=cfg["DB_USER"],
            password=cfg["DB_PASSWORD"],
            database=cfg["DB_NAME"],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)


def query_all(sql, params=None):
    """Run a SELECT and return all rows as a list of dicts."""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(sql, params or ())
        return cur.fetchall()


def query_one(sql, params=None):
    """Run a SELECT and return a single row (dict) or None."""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(sql, params or ())
        return cur.fetchone()


def execute(sql, params=None):
    """Run an INSERT/UPDATE/DELETE and return (rowcount, lastrowid)."""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(sql, params or ())
        return cur.rowcount, cur.lastrowid
