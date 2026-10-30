-- PostgreSQL DBA handoff for MedSupplier restore drill.
-- Replace the timestamp suffix before running.
-- Run as a PostgreSQL role allowed to create databases.

CREATE DATABASE medsupplier_restore_drill_YYYYMMDD_HHMMSS OWNER isosmart;

-- Optional verification:
-- SELECT datname, pg_catalog.pg_get_userbyid(datdba) AS owner
-- FROM pg_database
-- WHERE datname = 'medsupplier_restore_drill_YYYYMMDD_HHMMSS';
