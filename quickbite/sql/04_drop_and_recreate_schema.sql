-- Drop and recreate public schema
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

-- Grant all privileges to postgres
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
