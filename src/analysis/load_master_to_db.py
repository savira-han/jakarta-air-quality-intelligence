
from pathlib import Path
import duckdb

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# File paths
CSV_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "master_pm25_hourly.csv"
)

DATABASE_PATH = (
    PROJECT_ROOT
    / "database"
    / "air_quality.duckdb"
)


def load_master_data():

    # Check whether source CSV exists
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Master CSV not found: {CSV_PATH}"
        )

    # Connect to DuckDB
    con = duckdb.connect(str(DATABASE_PATH))

    try:
        print("Loading master CSV into DuckDB...")

        # Import CSV into DuckDB
        con.execute("""
            CREATE OR REPLACE TABLE master_pm25_hourly AS
            SELECT *
            FROM read_csv_auto(
                ?,
                header = true,
                sample_size = -1
            )
        """, [str(CSV_PATH)])

        # Verify record count
        total_records = con.execute("""
            SELECT COUNT(*)
            FROM master_pm25_hourly
        """).fetchone()[0]

        print(f"Successfully loaded {total_records:,} records.")

        # Display table schema
        print("\nTable schema:")

        schema = con.execute("""
            DESCRIBE master_pm25_hourly
        """).df()

        print(schema.to_string(index=False))

    finally:
        con.close()


if __name__ == "__main__":
    load_master_data()
