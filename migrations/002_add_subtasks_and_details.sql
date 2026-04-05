-- Migration: Add subtask and details support to tasks
-- Run this against your PostgreSQL database before deploying the updated code.

ALTER TABLE tasks ADD COLUMN IF NOT EXISTS parent_id TEXT REFERENCES tasks(id) ON DELETE CASCADE;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS details TEXT NOT NULL DEFAULT '';

-- Index for efficient subtask lookups
CREATE INDEX IF NOT EXISTS idx_tasks_parent_id ON tasks(parent_id);
