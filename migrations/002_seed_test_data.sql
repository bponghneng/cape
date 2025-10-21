-- Seed test data for cape_issues
-- This is optional test data for validating the workflow

INSERT INTO cape_issues (id, description, status) VALUES
(1, 'Fix login page CSS styling issues', 'pending'),
(2, 'Add user profile photo upload feature', 'started'),
(3, 'Refactor authentication module to use JWT', 'completed');

-- To clear test data, run:
-- DELETE FROM cape_issues WHERE id IN (1, 2, 3);
