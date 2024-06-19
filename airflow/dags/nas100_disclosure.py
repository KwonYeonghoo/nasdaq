from airflow import DAG
from airflow.hooks.base import BaseHook
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
import json
import os
import pymysql
from sec_api import ExtractorApi
import google.generativeai as genai
import pandas as pd
import boto3
import time


companies = {
    'MSFT': 'microsoft-corp',
    'AAPL': 'apple-computer-inc'
}

tickers = list(companies.keys())

forms = ['10-Q', '10-K']

# variable 생성해줘야 함.
GEM_API_KEY = Variable.get('gem_api_key')
BUCKET_NAME = Variable.get('bucket_name')
api_keys = Variable.get('api_keys')

genai.configure(api_key=GEM_API_KEY)
genai.GenerationConfig(max_output_tokens=2048)
MODEL = genai.GenerativeModel('gemini-pro')



# 텍스트 데이터를 지정된 파일에 저장
def save_to_txt(filename, text):
    # 디렉토리 경로를 추출
    directory = os.path.dirname(filename)
    
    # 디렉토리가 존재하지 않으면 생성
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(filename, 'w') as file:
        file.write(text)
        

# JSON 파일에서 EDGAR 보고서 URL을 읽어와서 10-Q 및 10-K 보고서의 특정 섹션을 추출하여 로컬 디렉토리(./reports/{ticker}/{form}/)에 텍스트 파일로 저장
# local 경로 바꿔야 됨(./data/...)
def extract_and_save_reports():
    with open('combined_file.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    pointer = 0
    count = 0
    for ticker in tickers:
        
        if count >= 98:
            count = 0
            pointer += 1

        extractor = ExtractorApi(api_keys[pointer])

        for form in forms:
            try:
                filing_url = data[ticker][0][form]
                if form == '10-Q':
                    part1item2 = extractor.get_section(filing_url, "part1item2", "text")
                    count += 1
                    part2item1a = extractor.get_section(filing_url, "part2item1a", "text")
                    count += 1
                    save_to_txt(f".data/reports/{ticker}/{form}/part1item2.txt", part1item2)
                    save_to_txt(f".data/reports/{ticker}/{form}/part2item1a.txt", part2item1a)
                else:
                    part1item1 = extractor.get_section(filing_url, "1", "text")
                    count += 1
                    part1item1a = extractor.get_section(filing_url, "1A", "text")
                    count += 1
                    part2item7 = extractor.get_section(filing_url, "7", "text")
                    count += 1
                    save_to_txt(f".data/reports/{ticker}/{form}/part1item1.txt", part1item1)
                    save_to_txt(f".data/reports/{ticker}/{form}/part2item1a.txt", part1item1a)
                    save_to_txt(f".data/reports/{ticker}/{form}/part2item7.txt", part2item7)
            except Exception as e:
                print(e)
                pass
            
            
# MySQL 함수 선언
def mysql_connection():
    connection=BaseHook.get_connection('mysql')
    conn = pymysql.connect(
            host=connection.host,
            user=connection.login,
            password=connection.password,
            db=connection.schema,
            port=int(connection.port)
    )
    return conn

def insert_data(conn, SQL, *args):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(SQL, args)
    conn.commit()

# S3
def s3_connection():
    connection = BaseHook.get_connection('airflow_s3')
    s3_client = boto3.client('s3',
                             aws_access_key_id=connection.login,
                             aws_secret_access_key=connection.password,
                             region_name=connection.extra_dejson.get('region_name'))
    print("S3 bucket connected!")
    return s3_client

def upload_to_s3(client, article, bucket_name, file_name):
    try:
        client.put_object(Bucket=bucket_name, Key=file_name, Body=bytes(article, 'utf-8'))
        print(f"Successfully uploaded {file_name} to {bucket_name}")
    except Exception as e:
        print(f"Failed to upload {file_name} to {bucket_name}: {e}")
        raise
    
def read_text_from_s3(client, bucket_name, file_name):
    response = client.get_object(Bucket=bucket_name, Key=file_name)
    text_data = response['Body'].read().decode('utf-8')
    return f"{text_data}\n\n"


# 주어진 EDGAR 보고서 텍스트를 요약, 요약 내용 S3 버킷에 업로드
def summarize_article(article, ticker, form, text, s3_client):
    prompt = f"""
    I would like you to summarize the provided EDGAR reports of {ticker} in a concise and objective way, mainly focusing on the impact on {ticker}'s stock.

    Followings are rules you must follow when generating an answer.
    1. Summary should include the key "risk factors", and "management discussion and analysis of financial condition and results of operations" of {ticker}
    2. Do NOT start with an opening sentence, just give me the answer right away.
    3. The answer MUST be in Korean.
    4. When translating into Korean, you must end each sentence with period(.).

    article:
    {article}
    """
    try:
        summary = MODEL.generate_content(prompt).text
        upload_to_s3(s3_client, summary, BUCKET_NAME, f"EDGAR/summary/{ticker}/type={form}/{text}")
        return summary
    
    except Exception as e:
        print(f"Failed to summarize article: {e}")
        return "오류 발생"


###

# 원문 S3적재
# 로컬 디렉토리에 저장된 모든 보고서 파일을 S3에 적재
def process_reports():
    s3_client = boto3.client('s3')
    # 현재 경로를 가져옴
    current_path = ".data//EDGAR/reports"

    # 현재 경로에 있는 모든 파일과 디렉토리를 가져옴
    all_tickers = os.listdir(current_path)
    for ticker in all_tickers:
        if ticker != ".DS_Store":
            cur_path = os.path.join(current_path, ticker)
            all_reports = os.listdir(cur_path)
            for report in all_reports:
                if report != ".DS_Store":
                    cur_path2 = os.path.join(cur_path, report)
                    all_texts = os.listdir(cur_path2)
                    for text in all_texts:
                        final_path = os.path.join(cur_path2, text)
                        upload_to_s3(s3_client, final_path, BUCKET_NAME, f"EDGAR/reports/{ticker}/type={report}/{text}")


# 요약본 DB & S3적재
# 로컬 디렉토리에서 모든 보고서 파일을 읽어와서 요약한 후, MySQL 데이터베이스에 저장(If 요약 내용X, 기본 메시지를 삽입)
def save_summaries_to_db():
    s3_client = s3_connection()
    current_path = "./data/EDGAR/reports"
    
    # 현재 경로를 가져옴
    conn = mysql_connection()
    
    # SQL 쿼리 선언
    SQL2_INSERT = '''
    INSERT INTO edgar_reports (date, ticker, name, summary_10q, summary_10k) VALUES (%s, %s, %s, %s, %s);
    '''
    
    SQL2_UPDATE = '''
    UPDATE edgar_reports
    SET summary_10q = %s, summary_10k = %s
    WHERE ticker = %s AND date = %s;
    '''

    # 현재 경로에 있는 모든 파일과 디렉토리를 가져옴
    all_tickers = os.listdir(current_path)
    for ticker in all_tickers:
        if ticker != ".DS_Store":
            cur_path = os.path.join(current_path, ticker)
            all_reports = os.listdir(cur_path)
            for report in all_reports:
                if report != ".DS_Store":
                    cur_path2 = os.path.join(cur_path, report)
                    all_texts = os.listdir(cur_path2)
                    for text in all_texts:
                        # final_path = os.path.join(cur_path2, text)
                        article = read_text_from_s3(s3_client, BUCKET_NAME, f"EDGAR/reports/{ticker}/type={report}/{text}")
                        date = datetime.now().strftime("%Y-%m-%d")
                        name = companies[ticker]
                        summary_10q, summary_10k = "", ""
                        if report == "10-Q":
                            summary_10q += summarize_article(article, ticker, report, text, s3_client)
                        else:
                            summary_10k += summarize_article(article, ticker, report, text, s3_client)
                        time.sleep(3)
                        
            if summary_10q == "":
                summary_10q = "발행된 10-Q 분기리포트가 없습니다!"
            if summary_10k == "":
                summary_10k = "발행된 10-K 연간리포트가 없습니다!"

            try:
                with conn.cursor() as cursor:
                    # 데이터베이스에 해당 ticker의 데이터가 있는지 확인
                    cursor.execute("SELECT COUNT(*) FROM edgar_reports WHERE ticker = %s AND date = %s", (ticker, date))
                    result = cursor.fetchone()
                    
                    if result[0] == 0:
                        # 데이터가 없는 경우 삽입
                        insert_data(conn, SQL2_INSERT, date, ticker, name, summary_10q, summary_10k)
                    else:
                        # 데이터가 있는 경우 업데이트
                        cursor.execute(SQL2_UPDATE, (name, summary_10q, summary_10k, ticker, date))
                        conn.commit()
                        print(f"{ticker} data updated for date {date}")
                        
            except Exception as e:
                print(f"Failed to insert/update data for {ticker}: {e}")
                conn.rollback()
    
    conn.close()
