-- FabriX-QA PostgreSQL Initialization
-- This script runs on first container startup.
-- Tables are created by Alembic migrations — this file handles extensions only.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search on defect types
