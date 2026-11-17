
from pathlib import Path
import duckdb

# Project directories
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_DIR = PROJECT_ROOT / "database"
DATABASE_PATH = DATABASE_DIR / "air_quality.duckdb"

# Create database directory if it doesn't exist
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

# Connect to DuckDB
def get_connection():
    con = duckdb.connect(str(DATABASE_PATH))
    return con


if __name__ == "__main__":
    con = get_connection()

    print("DuckDB connection successful!")
    print(f"Database location: {DATABASE_PATH}")

    con.close()
