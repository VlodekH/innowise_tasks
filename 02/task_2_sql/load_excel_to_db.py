import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from pathlib import Path

load_dotenv()

FILE_PATH = Path.cwd().parent / "data" / "task_2_data_ex.xlsx"
DB_USER = os.getenv("DB_USER", "me")
DB_PASSWORD = os.getenv("DB_PASSWORD", "changeme")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "innowise_db")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


def main() -> None:
    df = pd.read_excel(FILE_PATH)
    engine = create_engine(DATABASE_URL)

    df.to_sql(
        "bom_raw",
        engine,
        schema = "task_02",
        if_exists="append",
        index=False,
    )
    print(f"Loaded {len(df)} rows into bom_raw")


if __name__ == "__main__":
    main()
