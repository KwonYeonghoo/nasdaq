import warnings
warnings.filterwarnings(action='ignore')
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import pymysql
import yfinance as yf
import FinanceDataReader as fdr
from airflow.hooks.base import BaseHook
# !pip install finance-datareader
# !pip install -U finance-datareader # 업데이트


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
    
    
# 나스닥 전 종목 종목코드 수집
def fetch_nasdaq_list():
    df_ndq = fdr.StockListing('NASDAQ')
    nasdaq_list = list(df_ndq['Symbol'])
    return nasdaq_list


# 필요한 데이터 다 존재하는 유효한 나스닥 종목들만 수집하는 함수
def get_valid_nasdaq(**kwargs):
    nasdaq_list = kwargs['task_instance'].xcom_pull(task_ids='fetch_nasdaq_list')
    
    nasdaq_dict = {}
    for idx, ticker in enumerate(nasdaq_list, start=1):
        if ticker == "^IXIC":
            tick = yf.Ticker(ticker)
            hist = tick.history(period="1mo")[-2:]
            prev = hist.iloc[0]["Close"]
            cur = hist.iloc[1]["Close"]
            fluc = round((cur - prev) / prev * 100, 2)
            
            name = "NASDAQ Index"
            industry = "NASDAQ Index"
            market_cap = 0
            per = 0
            psr = 0
            pbr = 0
            ev_ebitda = 0
            
            print(f"{idx} / {len(nasdaq_list)}")
            nasdaq_dict[ticker] = [name, industry, market_cap, per, psr, pbr, ev_ebitda, fluc]

            continue
        
        nasdaq = yf.Ticker(ticker)
        info = nasdaq.info
        try:
            name = info["shortName"]
        except:
            continue
            
        try:
            industry = f'{info["industry"]}/{info["sector"]}'
            industry = industry.replace(" & ", "-")
            industry = industry.replace("—", " - ")
        except:
            continue
            
        try:
            market_cap = round(info["marketCap"], 2)
        except:
            continue
            
        try:
            if info["trailingPE"] < 100:
                per = round(info["trailingPE"], 2)
            else: continue
        except:
            continue
    
        try:
            psr = round(info["priceToSalesTrailing12Months"], 2)
        except:
            continue
    
        try:
            pbr = round(info["priceToBook"], 2)
        except:
            continue
    
        try:
            ev_ebitda = round(info["enterpriseToEbitda"], 2)
        except:
            continue
        
        try:
            tick = yf.Ticker(ticker)
            hist = tick.history(period="1mo")[-2:]
            prev = hist.iloc[0]["Close"]
            cur = hist.iloc[1]["Close"]
            fluc = round((cur - prev) / prev * 100, 2)
        except:
            fluc = 0
            
        print(f"{idx} / {len(nasdaq_list)}")
        nasdaq_dict[ticker] = [name, industry, market_cap, per, psr, pbr, ev_ebitda, fluc]

    df = pd.DataFrame.from_dict(data=nasdaq_dict, orient='index', columns=['name', 'industry', 'market_cap', 'per', 'psr', 'pbr', 'ev/ebitda', 'fluc'])
    df = df.reset_index().rename(columns={'index': 'ticker'})
    df['per'] = df['per'].astype('float64')
    df['psr'] = df['psr'].astype('float64')
    df['fluc'] = df['fluc'].astype('float64')
    
    # # inf를 포함하는 행은 삭제
    df = df.drop(df[df['per']==np.inf].index).reset_index(drop=True)
    df = df.drop(df[df['psr']==np.inf].index).reset_index(drop=True)
    
    return df

# nasdaq_all
def save_nasdaq_data(**kwargs):
    connection = mysql_connection()
    
    dailydate = datetime.now().strftime("%Y-%m-%d")
        
    df = kwargs['task_instance'].xcom_pull(task_ids='get_valid_nasdaq')
    
    # SQL 구문 작성
    SQL9_INSERT = '''
    INSERT INTO nasdaq_all (ticker, dailydate, name, industry, market_cap, per, psr, pbr, ev_ebitda, fluc) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    
    SQL9_UPDATE = '''
    UPDATE nasdaq_all
    SET name = %s, industry = %s, market_cap = %s, per = %s, psr = %s, pbr = %s, ev_ebitda = %s, fluc = %s
    WHERE ticker = %s AND dailydate = %s
    '''

    with connection.cursor() as cursor:
        for i in range(len(df)):
            ticker = df.loc[i, "ticker"]
            name = df.loc[i, "name"]
            industry = df.loc[i, "industry"]
            market_cap = df.loc[i, "market_cap"]
            per = df.loc[i, "per"]
            psr = df.loc[i, "psr"]
            pbr = df.loc[i, "pbr"]
            ev_ebitda = df.loc[i, "ev/ebitda"]
            fluc = df.loc[i, "fluc"]
            
                    
            try:
                # 삽입을 시도
                cursor.execute(SQL9_INSERT, (ticker, dailydate, name, industry, market_cap, per, psr, pbr, ev_ebitda, fluc))
            except pymysql.err.IntegrityError as e:
                if e.args[0] == 1062:  # 중복 항목이 있을 경우
                    # 중복 항목을 업데이트
                    cursor.execute(SQL9_UPDATE, (name, industry, market_cap, per, psr, pbr, ev_ebitda, fluc, ticker, dailydate))
                else:
                    # 다른 오류가 발생할 경우 예외 발생
                    raise e
        
        connection.commit()
    print("NASDAQ 데이터 저장 완료")
    
# 산업군별로 이상치 제거한 후 평균 낸 데이터 industry테이블에 삽입
def save_industry_data(**kwargs):
    connection = mysql_connection()
    df = kwargs['task_instance'].xcom_pull(task_ids='get_valid_nasdaq')

    dailydate = datetime.now().strftime("%Y-%m-%d")
        
    industry_list = list(df['industry'].unique())
    
    SQL5_INSERT = '''
    INSERT INTO industry (industry, dailydate, avg_market_cap, avgper, avgpsr, avgpbr, avgev_ebitda, avg_fluc) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    '''
    
    SQL5_UPDATE = '''
    UPDATE industry
    SET avg_market_cap = %s, avgper = %s, avgpsr = %s, avgpbr = %s, avgev_ebitda = %s, avg_fluc = %s
    WHERE industry = %s AND dailydate = %s
    '''
    
    def get_clean_avg(values):
        Q1 = np.percentile(values, 25)
        Q3 = np.percentile(values, 75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        clean_values = values[(values >= lower_bound) & (values <= upper_bound)]
        return round(clean_values.mean(), 2)
    
    with connection.cursor() as cursor:
        for industry in industry_list:
            avgMarketCap = round(df[df['industry'] == industry]['market_cap'].mean())
            avgPER = get_clean_avg(np.array(df[df['industry'] == industry]['per']))
            avgPSR = get_clean_avg(np.array(df[df['industry'] == industry]['psr']))
            avgPBR = get_clean_avg(np.array(df[df['industry'] == industry]['pbr']))
            avgEV_EBITDA = get_clean_avg(np.array(df[df['industry'] == industry]['ev/ebitda']))
            avgFluc = round(df[df['industry'] == industry]['fluc'].mean(), 2)
            
            try:
                cursor.execute(SQL5_INSERT, (industry, dailydate, avgMarketCap, avgPER, avgPSR, avgPBR, avgEV_EBITDA, avgFluc))
            except pymysql.err.IntegrityError as e:
                if e.args[0] == 1062:  # 중복 항목이 있을 경우
                    cursor.execute(SQL5_UPDATE, (avgMarketCap, avgPER, avgPSR, avgPBR, avgEV_EBITDA, avgFluc, industry, dailydate))
                else:
                    raise e
        connection.commit()
    connection.close()
    print("산업 데이터 저장 완료")