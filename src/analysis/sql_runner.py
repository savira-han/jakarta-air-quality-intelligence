from pathlib import Path
import sys
import warnings
import pandas as pd

# Suppress internal pandas/duckdb deprecation warnings until upstream patches are released
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

from database import get_connection

# Project directories
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SQL_DIR = PROJECT_ROOT / "sql"

# Configure Pandas for clean table printing
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)
pd.set_option("display.colheader_justify", "left")


def run_sql_file(sql_filename):
    """
    Execute a SQL file using the project's DuckDB database.
    """
    sql_path = (SQL_DIR / sql_filename).resolve()

    if not sql_path.is_relative_to(SQL_DIR.resolve()):
        raise ValueError("SQL file must be inside the sql directory.")

    con = get_connection()

    try:
        print(f"\nExecuting: {sql_filename}")
        print("-" * 60)

        sql_query = sql_path.read_text(encoding="utf-8")
        result = con.execute(sql_query)

        # Display results if the query returns a result set
        if result.description:
            df = result.df()

            if df.empty:
                print("Query executed successfully. No records returned.")
            else:
                # Clean table formatting without row indices
                print(df.to_string(index=False))

        print("\nSQL execution completed successfully.")

    except Exception as e:
        print(f"\nSQL execution failed: {e}")
        raise

    finally:
        con.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/analysis/sql_runner.py <sql_filename>")
        sys.exit(1)

    run_sql_file(sys.argv[1])