"""Tests for Database Migrations, Connection, and CLI Table Schema."""

from backend.app.cli import ALL_TABLES, get_db_connection, get_table_counts


def test_postgres_connection_and_table_schema():
    """Verifies that PostgreSQL + PostGIS container is accessible and all tables exist."""
    conn = get_db_connection()
    try:
        counts = get_table_counts(conn)
        # Verify all 10 tables from README Section 3 are present
        for table in ALL_TABLES:
            assert table in counts, f"Table {table} missing from database"
        assert counts["aircraft"] >= 500
        assert counts["flight_track_points"] >= 100000
        assert counts["space_weather"] >= 100
        assert counts["incident_cases"] == 3
        # Precursor candidates table is NOT pre-seeded; only precursor scanner writes to it
        assert counts["precursor_candidates"] == 0
    finally:
        conn.close()

