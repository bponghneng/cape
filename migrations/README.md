# Supabase Migrations

## Prerequisites

- Supabase CLI installed: `brew install supabase/tap/supabase`
- Supabase project created
- Environment variables set in `.env` file

## Running Migrations

### Option 1: Using Supabase CLI

1. Link to your Supabase project:
   ```bash
   supabase link --project-ref your-project-ref
   ```

2. Apply migration:
   ```bash
   supabase db push
   ```

### Option 2: Manual SQL Execution

1. Navigate to your Supabase project dashboard
2. Go to SQL Editor
3. Copy and paste the contents of `001_create_cape_issues_tables.sql`
4. Execute the SQL

## Verification

After running migrations, verify tables exist:

```sql
SELECT * FROM cape_issues;
SELECT * FROM cape_comments;
```

## Seed Test Data (Optional)

To populate the database with test data for validation:

1. Run the seed data migration:
   ```bash
   # Using Supabase SQL Editor or psql
   psql -f migrations/002_seed_test_data.sql
   ```

2. Or execute manually in Supabase SQL Editor:
   ```sql
   INSERT INTO cape_issues (id, description, status) VALUES
   (1, 'Fix login page CSS styling issues', 'pending'),
   (2, 'Add user profile photo upload feature', 'started'),
   (3, 'Refactor authentication module to use JWT', 'completed');
   ```

3. To clear test data:
   ```sql
   DELETE FROM cape_issues WHERE id IN (1, 2, 3);
   ```
