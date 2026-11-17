from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "database" / "air_quality.duckdb"


def inspect_database():
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DATABASE_PATH}")

    con = duckdb.connect(str(DATABASE_PATH), read_only=True)

    try:
        # List all tables
        tables = con.execute("SHOW TABLES").fetchall()

        if not tables:
            print("No tables found in the database.")
            return

        print("Tables in air_quality.duckdb:")
        for (table_name,) in tables:
            count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            print(f"- {table_name} ({count:,} rows)")

    finally:
        con.close()


if __name__ == "__main__":
    inspect_database()
