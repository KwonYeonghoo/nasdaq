from datetime import datetime, timedelta
from airflow.operators.empty import EmptyOperator
from airflow import DAG
from airflow.operators.python import PythonOperator

# from Industrial_group_relationship_chart import fetch_nasdaq_list, fetch_industries_list, relationship, preprocessing_df, save_network_to_db, nasdaq100_tickers
from Industrial_group_relatioship_chart import save_network_to_db
from slack_alarm import slack_alert_relationship_chart

def create_dag4():
    default_args = {
        'owner': 'airflow',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(seconds=30),
    }

    dag = DAG(
        'nasdaq100_industrial_group_realationship_pipeline',
        default_args=default_args,
        description='산업군 관계도를 MySQL에 저장하는 파이프라인',
        schedule_interval='0 12 * * MON-FRI',
        start_date=datetime(2024,6,17),
        catchup=False,
    )

    start = EmptyOperator(task_id='start', dag=dag)


    save_to_db_task = PythonOperator(
        task_id='save_network_to_db',
        python_callable=save_network_to_db,
        provide_context=True,
        on_failure_callback=slack_alert_relationship_chart.slack_fail_alert,
        dag=dag,
    )

    start >> save_to_db_task
    
    return dag

    
dag = create_dag4()
    