-- Add title column to cape_issues table
ALTER TABLE cape_issues ADD COLUMN title TEXT;

-- Optional: Backfill title from description (first 50 chars) for existing issues
UPDATE cape_issues 
SET title = substring(description from 1 for 50) || '...'
WHERE title IS NULL;
