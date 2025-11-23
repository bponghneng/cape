-- Add raw, source, and type columns to cape_comments table
-- These columns provide richer metadata for comments:
-- - raw: JSONB column storing the raw agent output for debugging
-- - source: TEXT column identifying where the comment came from (e.g., "agent", "system")
-- - type: TEXT column identifying the comment type (e.g., "claudecode", "opencode", "workflow")

-- Add raw column with JSONB type, NOT NULL with default empty object
ALTER TABLE cape_comments
ADD COLUMN IF NOT EXISTS raw JSONB NOT NULL DEFAULT '{}'::jsonb;

-- Add source column as nullable TEXT (to allow existing rows)
ALTER TABLE cape_comments
ADD COLUMN IF NOT EXISTS source TEXT;

-- Add type column as nullable TEXT (to allow existing rows)
ALTER TABLE cape_comments
ADD COLUMN IF NOT EXISTS type TEXT;

-- Optional: Add indexes for query performance (commented out for now)
-- CREATE INDEX IF NOT EXISTS idx_cape_comments_source ON cape_comments(source);
-- CREATE INDEX IF NOT EXISTS idx_cape_comments_type ON cape_comments(type);