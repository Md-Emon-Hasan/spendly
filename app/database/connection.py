import sqlite3
import os
import re
from flask import g, current_app

# PostgreSQL support
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_PSYCHOG2 = True
except ImportError:
    HAS_PSYCHOG2 = False

class DBConnection:
    """A wrapper that handles both SQLite and PostgreSQL connections."""
    def __init__(self, connection, is_postgres=False):
        self.connection = connection
        self.is_postgres = is_postgres

    def execute(self, query, params=None):
        if self.is_postgres:
            # 1. Translate '?' to '%s'
            query = query.replace('?', '%s')
            # 2. Translate strftime('%Y-%m', date) to TO_CHAR(date, 'YYYY-MM')
            # Robust regex to handle variations in quotes and spacing
            query = re.sub(r"strftime\s*\(\s*['\"]%Y-%m['\"]\s*,\s*(.*?)\)", r"TO_CHAR(\1, 'YYYY-MM')", query)
            # 3. Translate strftime('%w', date) to EXTRACT(DOW FROM date)
            query = re.sub(r"strftime\s*\(\s*['\"]%w['\"]\s*,\s*(.*?)\)", r"(EXTRACT(DOW FROM \1)::int)", query)
            # 4. Handle simple date retrieval if used
            query = re.sub(r"strftime\s*\(\s*['\"]%Y-%m-%d['\"]\s*,\s*(.*?)\)", r"(\1)::date::text", query)
            
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        else:
            cursor = self.connection.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()

    def fetchone(self, cursor):
        return cursor.fetchone()

    def fetchall(self, cursor):
        return cursor.fetchall()

def get_db():
    if 'db' not in g:
        is_postgres = current_app.config.get('IS_POSTGRES', False)
        
        if is_postgres:
            if not HAS_PSYCHOG2:
                raise ImportError("PostgreSQL is requested but psycopg2 is not installed.")
            
            conn = psycopg2.connect(current_app.config['DATABASE_URI'])
            g.db = DBConnection(conn, is_postgres=True)
        else:
            # Fallback to local SQLite
            conn = sqlite3.connect(current_app.config['DATABASE_SQLITE'])
            conn.row_factory = sqlite3.Row
            g.db = DBConnection(conn, is_postgres=False)
            
    return g.db

def close_db(e=None):
    db_wrapper = g.pop('db', None)
    if db_wrapper is not None:
        db_wrapper.close()
