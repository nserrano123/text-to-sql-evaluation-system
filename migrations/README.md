# Database Migrations

This directory contains SQL migration scripts for the Text-to-SQL Evaluation System.

## Migration Files

- `001_initial_schema.sql` - Initial database schema with all tables, constraints, and indexes

## How to Apply Migrations

### Using Supabase Dashboard

1. Log in to your Supabase project dashboard
2. Navigate to the SQL Editor
3. Copy the contents of `001_initial_schema.sql`
4. Paste into the SQL Editor and click "Run"

### Using Supabase CLI

```bash
# Make sure you're logged in
supabase login

# Link to your project
supabase link --project-ref your-project-ref

# Apply the migration
supabase db push
```

### Using psql (Direct PostgreSQL Connection)

```bash
psql -h your-db-host -U postgres -d postgres -f migrations/001_initial_schema.sql
```

## Schema Overview

The migration creates the following tables:

1. **gold_queries** - Reference SQL queries (gold standard)
2. **evaluations** - Evaluation instances linking gold queries to generated SQL
3. **execution_accuracy** - Execution Accuracy (EX) metric data
4. **time_to_answer** - Time-to-Answer (TTA) metric data
5. **component_matching** - Component Matching metric with F1 scores

## Constraints and Validations

- All foreign keys use `ON DELETE CASCADE` for referential integrity
- Time validation: `end_time` must be greater than `start_time`
- Duration validation: `duration_seconds` must be non-negative
- F1 score validation: Must be between 0 and 1 (or NULL)

## Indexes

Indexes are created on:

- Primary keys (automatic)
- Foreign keys for join performance
- `evaluation_date` for temporal queries
- `is_correct` for filtering correct/incorrect evaluations
- `created_at` timestamps for audit queries

## Rollback

To rollback this migration, run:

```sql
DROP TABLE IF EXISTS component_matching CASCADE;
DROP TABLE IF EXISTS time_to_answer CASCADE;
DROP TABLE IF EXISTS execution_accuracy CASCADE;
DROP TABLE IF EXISTS evaluations CASCADE;
DROP TABLE IF EXISTS gold_queries CASCADE;
```

**Warning:** This will delete all data in these tables.
