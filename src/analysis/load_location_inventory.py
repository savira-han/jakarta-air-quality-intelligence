from pathlib import Path
import duckdb

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# File paths
CSV_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "openaq"
    / "location_inventory.csv"
)

DATABASE_PATH = (
    PROJECT_ROOT
    / "database"
    / "air_quality.duckdb"
)


def load_location_inventory():

    # Check whether source CSV exists
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Location inventory CSV not found: {CSV_PATH}"
        )

    # Ensure database directory exists
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Connect to DuckDB
    con = duckdb.connect(str(DATABASE_PATH))

    try:
        print("Loading location inventory CSV into DuckDB...")

        # Import CSV into DuckDB
        con.execute("""
            CREATE OR REPLACE TABLE location_inventory AS
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
            FROM location_inventory
        """).fetchone()[0]

        print(f"Successfully loaded {total_records:,} records.")

        # Display table schema
        print("\nTable schema:")

        schema = con.execute("""
            DESCRIBE location_inventory
        """).df()

        print(schema.to_string(index=False))

    finally:
        con.close()


if __name__ == "__main__":
    load_location_inventory()
