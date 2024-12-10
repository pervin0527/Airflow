from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email": ["airflow@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "number_counting_dag",
    default_args=default_args,
    description="A simple DAG to count numbers",
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 2, 12),
    catchup=False,
    tags=["example"],
) as dag:
    
    count_10 = BashOperator(
        task_id="count_10",
        bash_command="for i in {1..10}; do echo $i; sleep 1; TEST",
    )

    count_10 = BashOperator(
        task_id="count_10",
        bash_command="for i in {1..10}; do echo $i; sleep 1; done",
    )

    count_20 = BashOperator(
        task_id="count_20",
        bash_command="for i in {11..20}; do echo $i; sleep 1; done",
    )

    count_30 = BashOperator(
        task_id="count_30",
        bash_command="for i in {21..30}; do echo $i; sleep 1; done",
    )

    count_10 >> count_20 >> count_30