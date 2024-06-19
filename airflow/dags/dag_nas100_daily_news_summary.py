from datetime import datetime, timedelta
from airflow.operators.empty import EmptyOperator
from airflow import DAG
from airflow.operators.python import PythonOperator

from nas100_news_summary_metrics import execute, companies
from slack_alarm import slack_alert_nas100_daily_news_summary

def create_dag():
    default_args = {
        'owner': 'airflow',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(seconds=30),
    }

    dag = DAG(
        'nasdaq100_news_data_pipeline',
        default_args=default_args,
        description='뉴스 요약데이터가 S3와 MySQL에 저장하는 파이프라인',
        schedule_interval='0 20 * * MON-FRI',
        start_date=datetime(2024,6,17),
        catchup=False,
    )

    # Ticker
    tickers = list(companies.keys())

    start = EmptyOperator(task_id='start', dag=dag)
    
    # 나스닥100 각 뉴스 및 요약 저장하는 작업(DB&S3)
    save_news_summary_to_all = PythonOperator(
        task_id='save_news_summary',
        python_callable=execute,
        op_args=[tickers],
        on_failure_callback=slack_alert_nas100_daily_news_summary.slack_fail_alert,
        dag=dag,
    )

    # DAG 실행 순서
    start >> save_news_summary_to_all
    
    return dag

    
dag = create_dag()