
from datetime import datetime

import pandas as pd
from pymongo import MongoClient

from airflow.sdk import DAG, Asset, task
from airflow.hooks.base import BaseHook


PROCESSED_REVIEWS = Asset(
    "file:///opt/airflow/data/output/processed_reviews.csv"
)

INPUT_PATH = "/opt/airflow/data/output/processed_reviews.csv"


with DAG(
    dag_id="load_reviews_to_mongodb",
    start_date=datetime(2026, 1, 1),
    schedule=[PROCESSED_REVIEWS],
    catchup=False,
    tags=["reviews", "mongodb"],
) as dag:

    @task
    def load_reviews():
        # Read the Airflow Connection
        conn = BaseHook.get_connection("mongo_default")

        # Connect to MongoDB
        client = MongoClient(
            host=conn.host,
            port=conn.port,
            serverSelectionTimeoutMS=5000,
        )

        try:
            client.admin.command("ping")

            db = client[conn.schema or "reviews_db"]
            collection = db["reviews"]

            # Read the processed CSV
            df = pd.read_csv(INPUT_PATH)

            # Convert dates and ratings to suitable data types
            df["at"] = pd.to_datetime(df["at"], errors="coerce")
            df["score"] = pd.to_numeric(
                df["score"], errors="coerce"
            )

            # Replace missing values with None for MongoDB
            df = df.astype(object).where(pd.notna(df), None)

            # Convert Pandas timestamps to Python datetime objects
            df["at"] = df["at"].apply(
                lambda value: (
                    value.to_pydatetime()
                    if pd.notna(value) and value is not None
                    else None
                )
            )

            records = df.to_dict(orient="records")

            # Replace existing collection contents on each run
            collection.delete_many({})

            if records:
                collection.insert_many(records)

            print(f"Loaded {len(records)} reviews into MongoDB")

        finally:
            client.close()

    load_reviews()
