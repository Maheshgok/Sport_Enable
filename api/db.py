"""
Database connection and utilities for Moove API
Handles PostgreSQL connection pooling and query execution
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
import os
from contextlib import contextmanager

# Database configuration from environment variables
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': os.environ.get('DB_PORT', '5432'),
    'database': os.environ.get('DB_NAME', 'moove_db'),
    'user': os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASSWORD', ''),
}

# Connection pool (initialized when needed)
_connection_pool = None

def get_connection_pool():
    """Get or create database connection pool"""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            **DB_CONFIG
        )
    return _connection_pool

@contextmanager
def get_db_connection():
    """
    Context manager for database connections
    Usage:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users")
    """
    pool = get_connection_pool()
    conn = pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        pool.putconn(conn)

@contextmanager
def get_db_cursor(cursor_factory=RealDictCursor):
    """
    Context manager for database cursor (returns dict results by default)
    Usage:
        with get_db_cursor() as cur:
            cur.execute("SELECT * FROM users")
            users = cur.fetchall()
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=cursor_factory)
        try:
            yield cursor
        finally:
            cursor.close()

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """
    Execute a query and return results
    
    Args:
        query: SQL query string
        params: Query parameters (tuple or dict)
        fetch_one: Return single row
        fetch_all: Return all rows
        
    Returns:
        Query results or None
    """
    with get_db_cursor() as cur:
        cur.execute(query, params)
        
        if fetch_one:
            return cur.fetchone()
        elif fetch_all:
            return cur.fetchall()
        else:
            return None

def test_connection():
    """Test database connection"""
    try:
        with get_db_cursor() as cur:
            cur.execute("SELECT 1")
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
