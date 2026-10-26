
from datetime import datetime

from airflow.sdk import DAG, task, task_group, Asset
from airflow.providers.standard.sensors.filesystem import FileSensor


INPUT_PATH = "/opt/airflow/data/input/tiktok_google_play_reviews.csv"
OUTPUT_PATH = "/opt/airflow/data/output/processed_reviews.csv"
PROCESSED_REVIEWS = Asset(
    "file:///opt/airflow/data/output/processed_reviews.csv"
)

with DAG(
    dag_id="reviews_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["reviews"],
) as dag:

    wait_for_file = FileSensor(
        task_id="wait_for_file",
        filepath="tiktok_google_play_reviews.csv",
        fs_conn_id="fs_default",
        poke_interval=10,
        timeout=3600,
        mode="reschedule",
    )

    @task.branch
    def check_file():
        import os

        if not os.path.exists(INPUT_PATH) or os.path.getsize(INPUT_PATH) == 0:
            return "empty_file"

        return "group_task.replace_nulls"

    @task
    def empty_file():
        print("The input file is empty.")

    @task_group(group_id="group_task")
    def group_task():
        import pandas as pd
        import emoji

        @task
        def replace_nulls():
            df = pd.read_csv(INPUT_PATH, keep_default_na=False)
            df = df.replace("null", "-")
            return df.to_json(orient="records")

        @task
        def sort_by_date(data):
            import json

            df = pd.DataFrame(json.loads(data))
            df["at"] = pd.to_datetime(df["at"], errors="coerce")
            df = df.sort_values("at", na_position="last")
            return df.to_json(orient="records", date_format="iso")

        @task(
            outlets = [PROCESSED_REVIEWS]
        )
        def remove_emojis(data):
            import json
            import os

            df = pd.DataFrame(json.loads(data))
            df["content"] = df["content"].apply(
                lambda value: emoji.replace_emoji(str(value), replace="")
            )

            os.makedirs("/opt/airflow/data/output", exist_ok=True)
            df.to_csv(OUTPUT_PATH, index=False)
            print(f"Processed {len(df)} rows. Saved to {OUTPUT_PATH}")

        cleaned = replace_nulls()
        sorted_data = sort_by_date(cleaned)
        remove_emojis(sorted_data)

    branch = check_file()
    empty = empty_file()
    transformations = group_task()

    wait_for_file >> branch
    branch >> empty
    branch >> transformations
