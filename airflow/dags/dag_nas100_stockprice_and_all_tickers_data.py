from datetime import datetime, timedelta
from airflow.operators.empty import EmptyOperator
from airflow import DAG
from airflow.operators.python import PythonOperator
from nas100_daily_stockprice import insert_data, companies
from all_industries_finance_metrics import fetch_nasdaq_list, get_valid_nasdaq, save_nasdaq_data, save_industry_data
from slack_alarm import slack_alert_nas100_stockprice_and_all_tickers_data

def create_dag2():
    default_args = {
        'owner': 'airflow',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(seconds=30),
    }

    dag = DAG(
        'nasdaq100_stockprice_and_nasdaq_all_data_pipeline',
        default_args=default_args,
        description='나스닥100 일별주가와 전 종목 재무지표를 MySQL에 저장하는 파이프라인',
        schedule_interval='0 20 * * MON-FRI',
        start_date=datetime(2024,6,17),
        catchup=False,
    )

    # Ticker
    tickers = list(companies.keys())

    start = EmptyOperator(task_id='start', dag=dag)
     
    # 나스닥100 일별주가 저장하는 작업
    save_stockprice_to_db = PythonOperator(
        task_id='Insert_stockprice_data',
        python_callable=insert_data,
        op_args=[tickers],
        on_failure_callback=slack_alert_nas100_stockprice_and_all_tickers_data.slack_fail_alert,
        on_success_callback=slack_alert_nas100_stockprice_and_all_tickers_data.slack_success_alert,
        dag=dag,
    )
    
    # 나스닥 전종목 수집 작업(이거 select_valid_nasdaq 옮겨도 됨)
    select_nasdaq = PythonOperator(
        task_id='fetch_nasdaq_list',
        python_callable=fetch_nasdaq_list,
        on_failure_callback=slack_alert_nas100_stockprice_and_all_tickers_data.slack_fail_alert,
        dag=dag,
    )

    # 유효(필요데이터 전부 있는) 나스닥 종목 수집 작업
    select_valid_nasdaq = PythonOperator(
        task_id='get_valid_nasdaq',
        python_callable=get_valid_nasdaq,
        provide_context=True,
        on_failure_callback=slack_alert_nas100_stockprice_and_all_tickers_data.slack_fail_alert,
        dag=dag,
    )

    # nasdaq_all Table
    save_nasdaq_data_to_db = PythonOperator(
        task_id='save_nasdaq_data',
        python_callable=save_nasdaq_data,
        provide_context=True,
        on_failure_callback=slack_alert_nas100_stockprice_and_all_tickers_data.slack_fail_alert,
        dag=dag,
    )

    # industry Table
    save_industry_data_to_db = PythonOperator(
        task_id='save_industry_data',
        python_callable=save_industry_data,
        provide_context=True,
        on_failure_callback=slack_alert_nas100_stockprice_and_all_tickers_data.slack_fail_alert,
        dag=dag,
    )
    

    # DAG 실행 순서
    start >> save_stockprice_to_db >> select_nasdaq >> select_valid_nasdaq >> [save_nasdaq_data_to_db, save_industry_data_to_db]
    
    return dag

    
dag = create_dag2()