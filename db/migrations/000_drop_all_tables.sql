DO $$
DECLARE
    rec RECORD;
BEGIN
    -- Drop all tables in the public schema
    FOR rec IN (
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
    ) LOOP
        EXECUTE 'DROP TABLE IF EXISTS public.' || quote_ident(rec.tablename) || ' CASCADE';
    END LOOP;

    -- Drop all sequences in the public schema
    FOR rec IN (
        SELECT sequencename
        FROM pg_sequences
        WHERE schemaname = 'public'
    ) LOOP
        EXECUTE 'DROP SEQUENCE IF EXISTS public.' || quote_ident(rec.sequencename) || ' CASCADE';
    END LOOP;
    END $$;