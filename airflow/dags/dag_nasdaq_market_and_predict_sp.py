from datetime import datetime, timedelta
from airflow.operators.empty import EmptyOperator
from airflow import DAG
from airflow.operators.python import PythonOperator

from daily_market import scrape_data, markets
from predict_model import predict_stock_prices, save_predict_stockprice_to_db, com
from slack_alarm import slack_alert_nasdaq_market_and_predict_sp

def create_dag3():
    default_args = {
        'owner': 'airflow',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(seconds=30),
    }

    dag = DAG(
        'nasdaq_market_data_and_predict_stock_prices_pipeline',
        default_args=default_args,
        description='선물, 세계지수 등 시장지표와 주가 예측 데이터를 MySQL에 저장하는 파이프라인',
        schedule_interval='0 20 * * MON-FRI',
        start_date=datetime(2024,6,17),
        catchup=False,
    )

    start = EmptyOperator(task_id='start', dag=dag)

    # 시장지표
    select_daily_market = PythonOperator(
        task_id='save_daily_market',
        python_callable=scrape_data,
        op_args=[markets],
        on_failure_callback=slack_alert_nasdaq_market_and_predict_sp.slack_fail_alert,
        dag=dag,
    )
    
    predict_stock_prices_task = PythonOperator(
        task_id='predict_stock_prices',
        python_callable=predict_stock_prices,
        op_args=[com],
        on_failure_callback=slack_alert_nasdaq_market_and_predict_sp.slack_fail_alert,
        dag=dag,
    )

    save_predictions_to_sql_task = PythonOperator(
        task_id='save_predictions_to_sql',
        python_callable=save_predict_stockprice_to_db,
        on_failure_callback=slack_alert_nasdaq_market_and_predict_sp.slack_fail_alert,
        dag=dag,
    )

    # DAG 실행 순서
    start >> select_daily_market >> predict_stock_prices_task >> save_predictions_to_sql_task

    
    return dag

    
dag = create_dag3()
    