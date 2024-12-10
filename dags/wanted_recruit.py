import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

import pytz

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from projects.wanted_recruit.modules.wanted_recruit_raw_data_crawler import wanted_crawling
from projects.wanted_recruit.modules.wanted_recruit_api_process import run_async_wanted_process

# 한국 시간대 설정
KST = pytz.timezone("Asia/Seoul")

# DAG의 시작일을 과거의 고정된 날짜로 설정 (예: 2024년 1월 1일)
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ["airflow@example.com"],
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(minutes=2880),
    'start_date': datetime(2024, 1, 1, 3, 0, tzinfo=KST),  # 2024년 1월 1일 새벽 3시로 고정
}

dag = DAG(
    dag_id='wanted_recruitments',
    default_args=default_args,
    description='Processing of Wanted recruit data',
    schedule_interval='0 3 */2 * *',  # 이틀마다 새벽 3시에 실행
    max_active_runs=1,  # 동시 실행 제한
    catchup=False,  # 과거의 실행되지 않은 구간을 실행하지 않음
    is_paused_upon_creation=False,
    tags=['wanted', 'recruit', 'crawl', 'process']
    # tags=['wanted', 'recruit', 'crawl']
)

with dag:
    # 크롤링 태스크
    crawl_task = PythonOperator(
        task_id='wanted_crawl_data',
        python_callable=wanted_crawling,
        provide_context=True,
        retry_delay=timedelta(minutes=5),
        retries=2,
    )

    # 데이터 처리 태스크
    process_task = PythonOperator(
        task_id='wanted_recruit_parsing',
        python_callable=run_async_wanted_process,
        provide_context=True,
        retry_delay=timedelta(minutes=5),
        retries=2,
    )

    # 태스크 순서 정의
    crawl_task >> process_task