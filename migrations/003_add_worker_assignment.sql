-- Migration: Add Worker Assignment Support
-- Description: Adds worker assignment functionality to enable multiple workers to process issues without conflicts

-- Create enum type for worker IDs
CREATE TYPE worker_id AS ENUM ('alleycat-1', 'tydirium-1');

-- Add assigned_to column to track which worker is processing an issue
ALTER TABLE cape_issues
ADD COLUMN assigned_to worker_id;

-- Create index for performance on worker assignment queries
CREATE INDEX idx_cape_issues_assigned_to ON cape_issues(assigned_to);

-- Create PostgreSQL function for atomic issue locking
-- This function atomically retrieves and locks the next pending issue
-- Uses FOR UPDATE SKIP LOCKED to prevent race conditions between workers
CREATE OR REPLACE FUNCTION get_and_lock_next_issue(p_worker_id worker_id)
RETURNS TABLE (issue_id INTEGER, issue_description TEXT) AS $$
BEGIN
    RETURN QUERY
    UPDATE cape_issues
    SET status = 'started', assigned_to = p_worker_id, updated_at = now()
    WHERE cape_issues.id = (
        SELECT id FROM cape_issues WHERE status = 'pending'
        ORDER BY created_at ASC FOR UPDATE SKIP LOCKED LIMIT 1
    )
    RETURNING cape_issues.id, cape_issues.description;
END;
$$ LANGUAGE plpgsql;
