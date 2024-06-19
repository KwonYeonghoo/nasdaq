# from airflow.hooks.base import BaseHook
# from airflow.providers.slack.operators.slack import SlackAPIPostOperator


# class SlackAlert:
#     def __init__(self, channel):
#         self.slack_channel = channel
#         self.slack_conn_id = BaseHook.get_connection('slack').conn_id
#         self.slack_token = BaseHook.get_connection('slack').password
        

#     def slack_fail_alert(self, context):
#         # 실패한 태스크 추출
#         task_instance = context.get('task_instance')
#         task_id = task_instance.task_id
#         dag_id = context.get('task_instance').dag_id
#         execution_date = context.get('execution_date')
#         log_url = task_instance.log_url
        
#         # Slack에 전송할 메시지
#         msg = """
#             :red_circle: Task Failed.
#             *Task*: {task}
#             *Dag*: {dag}
#             *Execution Time*: {exec_date}
#             *Log Url*: {log_url}
#         """.format(
#             task=task_id,
#             dag=dag_id,
#             exec_date=execution_date,
#             log_url=log_url
#         )
        
#         # 메세지 전송
#         alert = SlackAPIPostOperator(
#             task_id='slack_failed_{dag_id}_{task_id}',
#             channel=self.slack_channel,
#             token=self.slack_token,
#             text=msg
#         )
        
#         alert.execute(context=context)

from airflow.hooks.base import BaseHook
from airflow.providers.slack.operators.slack import SlackAPIPostOperator
from datetime import datetime

class SlackAlert:
    def __init__(self, channel):
        self.slack_channel = channel
        self.slack_conn_id = 'slack'
        # self.slack_token = BaseHook.get_connection('slack').password

    def slack_fail_alert(self, context):
        # 실패한 태스크 추출
        task_instance = context.get('task_instance')
        task_id = task_instance.task_id
        dag_id = context.get('task_instance').dag_id
        execution_date = context.get('execution_date')
        log_url = task_instance.log_url
        
        # Slack에 전송할 메시지
        msg = """
            :red_circle: Task Failed.
            *Task*: {task}
            *Dag*: {dag}
            *Execution Time*: {exec_date}
            *Log Url*: {log_url}
        """.format(
            task=task_id,
            dag=dag_id,
            exec_date=execution_date,
            log_url=log_url
        )
        
        # 메세지 전송
        self._send_slack_message(msg)

    def slack_success_alert(self, context):
        # 성공한 태스크 추출
        task_instance = context.get('task_instance')
        task_id = task_instance.task_id
        dag_id = context.get('task_instance').dag_id
        execution_date = context.get('execution_date')
        log_url = task_instance.log_url
        
        # Slack에 전송할 메시지
        msg = """
            :white_check_mark: Task Succeeded.
            *Task*: {task}
            *Dag*: {dag}
            *Execution Time*: {exec_date}
            *Log Url*: {log_url}
        """.format(
            task=task_id,
            dag=dag_id,
            exec_date=execution_date,
            log_url=log_url
        )
        
        # 메세지 전송
        self._send_slack_message(msg)
    
    def _send_slack_message(self, msg):
        alert = SlackAPIPostOperator(
            task_id=f'slack_alert_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            channel=self.slack_channel,
            token=self.slack_token,
            text=msg
        )
        
        alert.execute(context={})
     

    
# 각 DAG의 SlackAlert 인스턴스를 생성
slack_alert_nas100_daily_news_summary = SlackAlert(channel='#airflow-logs-alarm')
slack_alert_nas100_stockprice_and_all_tickers_data = SlackAlert(channel='#airflow-logs-alarm')
slack_alert_nasdaq_market_and_predict_sp = SlackAlert(channel='#airflow-logs-alarm')
slack_alert_relationship_chart = SlackAlert(channel='#airflow-logs-alarm')