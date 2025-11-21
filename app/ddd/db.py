"""
BOOK: SEA-SEC Book of Records

CHAPTER 1: Purpose
  V1  Open the library (Postgres).
  V2  Make sure shelves (tables) exist.

CHAPTER 2: Tables
  V1  page_screenshots -> images and notes per URL.
  V2  run_reports      -> one row per test run, with pass/fail and tier.
  V3  findings         -> each specific issue from a run.
"""

import os
from psycopg_pool import ConnectionPool

DATABASE_URL = os.getenv("DATABASE_URL")

pool = ConnectionPool(
    DATABASE_URL,
    min_size=1,
    max_size=5,
    kwargs={"autocommit": True},
)

def migrate_once():
    with pool.connection() as conn, conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS page_screenshots (
          id BIGSERIAL PRIMARY KEY,
          url TEXT NOT NULL,
          status TEXT NOT NULL,
          http_status INT,
          captured_at TIMESTAMPTZ NOT NULL DEFAULT now(),
          image_bytes BYTEA,
          image_format TEXT DEFAULT 'png',
          notes JSONB
        );""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS run_reports (
          id BIGSERIAL PRIMARY KEY,
          run_id UUID NOT NULL,
          started_at TIMESTAMPTZ NOT NULL,
          finished_at TIMESTAMPTZ,
          target_url TEXT NOT NULL,
          pass BOOLEAN NOT NULL,
          overall_tier SMALLINT NOT NULL,
          totals JSONB,
          notes JSONB
        );""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS findings (
          id BIGSERIAL PRIMARY KEY,
          run_id UUID NOT NULL,
          url TEXT,
          ip INET,
          category TEXT,
          severity SMALLINT,
          tier SMALLINT,
          detail JSONB,
          created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );""")
