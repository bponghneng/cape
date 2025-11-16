-- Migration: Restrict worker locking to assigned issues
-- Description: Ensure workers only pull issues explicitly assigned to them

CREATE OR REPLACE FUNCTION get_and_lock_next_issue(p_worker_id worker_id)
RETURNS TABLE (issue_id INTEGER, issue_description TEXT) AS $$
BEGIN
    RETURN QUERY
    UPDATE cape_issues
    SET status = 'started',
        assigned_to = p_worker_id,
        updated_at = now()
    WHERE cape_issues.id = (
        SELECT id
        FROM cape_issues
        WHERE status = 'pending'
          AND assigned_to = p_worker_id
        ORDER BY created_at ASC
        FOR UPDATE SKIP LOCKED
        LIMIT 1
    )
    RETURNING cape_issues.id, cape_issues.description;
END;
$$ LANGUAGE plpgsql;
