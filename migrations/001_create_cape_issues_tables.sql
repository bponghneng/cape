-- Create cape_issues table
CREATE TABLE IF NOT EXISTS cape_issues (
    id SERIAL PRIMARY KEY,
    description TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'started', 'completed')),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Create cape_comments table
CREATE TABLE IF NOT EXISTS cape_comments (
    id SERIAL PRIMARY KEY,
    issue_id INT NOT NULL REFERENCES cape_issues(id) ON DELETE CASCADE,
    comment TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_cape_issues_status ON cape_issues(status);
CREATE INDEX IF NOT EXISTS idx_cape_comments_issue_id ON cape_comments(issue_id);

-- Create updated_at trigger for cape_issues
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_cape_issues_updated_at BEFORE UPDATE ON cape_issues
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
