import pandas as pd
import numpy as np
import yfinance as yf
import FinanceDataReader as fdr
from datetime import datetime

import pymysql
from airflow.hooks.base import BaseHook

# 나스닥 TOP100
nasdaq100_tickers = ['MSFT','AAPL','NVDA','GOOG','GOOGL','AMZN','META','AVGO','TSLA','ASML','COST','PEP','NFLX','AZN','AMD','LIN','ADBE','TMUS',
 'CSCO','QCOM','INTU','PDD','AMAT','TXN','CMCSA','AMGN','ISRG','INTC','HON','MU','BKNG','LRCX','VRTX','ADP','REGN','ABNB','ADI','MDLZ',
 'PANW','KLAC','SBUX','GILD','SNPS','CDNS','MELI','CRWD','PYPL','MAR','CTAS','CSX','WDAY','NXPI','ORLY','CEG','PCAR','MNST','MRVL','ROP',
 'CPRT','DASH','DXCM','FTNT','MCHP','AEP','KDP','ADSK','TEAM','LULU','KHC','PAYX','ROST','MRNA','DDOG','TTD','ODFL','FAST','IDXX','EXC',
 'CHTR','CSGP','GEHC','FANG','EA','VRSK','CCEP','CTSH','BKR','BIIB','XEL','ON','CDW','ANSS','MDB','DLTR','ZS','GFS','TTWO','ILMN','WBD',
 'WBA','SIRI']

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
    nasdaq_df_raw = fdr.StockListing('NASDAQ')
    nasdaq_list = list(nasdaq_df_raw['Symbol'])
    return nasdaq_list

# # nasdaq100 종목에만 존재하는 산업군들
def fetch_industries_list(nasdaq100_tickers=nasdaq100_tickers):
    nasdaq100_industries = []
    for ticker in nasdaq100_tickers:
        try:
            data = yf.Ticker(ticker)
            industry = f"{data.info['industry']}/{data.info['sector']}"
            sector = data.info.get('sector')
            if industry and sector:
                nasdaq100_industries.append(industry)
        except KeyError:
            print(f"KetError: 'sector' not found for {ticker}")
            continue
    nasdaq100_industries = list(set(nasdaq100_industries))
    return nasdaq100_industries


def relationship():
    # nasdaq_list=kwargs['task_instance'].xcom_pull(task_ids='fetch_nasdaq_list')
    nasdaq_list = fetch_nasdaq_list()
    
    stock_data = pd.DataFrame(columns=["Ticker", "Date", "Industry_Sector", "Open", "High", "Low", "Volume", "Close", "Close2", "Percentage_Change"])

    for idx, ticker in enumerate(nasdaq_list, start=1):
        try:
            data = yf.Ticker(ticker)
            df = data.history(period="ytd")
            
            msft_len = len(yf.Ticker("MSFT").history(period="ytd"))         
            if len(df) != msft_len:
                print(f"{idx} / {len(nasdaq_list)}: Data length mismatch for {ticker}")
                continue

            df = df.reset_index()[["Date", "Open", "High", "Low", "Close", "Volume"]]
            df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
            df["Ticker"] = ticker
            df["Close2"] = df["Close"].shift(-1) # 한 행 씩 위로 이동
            df["Percentage_Change"] = (df["Close2"] - df["Close"]) / df["Close"] * 100 # 전날 대비 등락률 구하기

            # 산업군 추가
            sector = data.info["sector"]
            industry = data.info["industry"]
            
            if sector is None or industry is None:
                print(f"{idx} / {len(nasdaq_list)}: No sector or industry information available for {ticker}")
                continue
            
            df["Industry_Sector"] = f"{industry}/{sector}"

            # 보기 좋게 컬럼 순서 변경
            new_order = ["Ticker", "Date", "Industry_Sector", "Open", "High", "Low", "Volume", "Close", "Close2", "Percentage_Change"]
            df = df[new_order]
            df = df[:-1] # 마지막 행은 NaN이므로 삭제

            if (df["Percentage_Change"].isna().sum() > 0) or ():
                print(f"{idx} / {len(nasdaq_list)}: NaN values found in Percentage_Change column for {ticker}")
                continue

            stock_data = pd.concat([stock_data, df], axis=0)
            print(f"{idx} / {len(nasdaq_list)} === {ticker}")

        except KeyError as e:
            print(f"{idx} / {len(nasdaq_list)}: KeyError fetching data for {ticker}: {e}")
            continue

        except Exception as e:
            print(f"{idx} / {len(nasdaq_list)}: Error fetching data for {ticker}: {e}")
            continue
        
    pivoted_stock_data = stock_data.pivot_table(index=['Industry_Sector'], columns='Date', values='Percentage_Change')

    pivoted_stock_data.columns.name = None
    pivoted_stock_data = pivoted_stock_data.reset_index()
    pivoted_stock_data = pivoted_stock_data.ffill(axis=1)
    
    return pivoted_stock_data


def save_network_to_db():
    today = datetime.now().strftime("%Y-%m-%d")
    
    # nasdaq100_industries = kwargs['task_instance'].xcom_pull(task_ids='fetch_industries_list')
    nasdaq100_industries = fetch_industries_list()
    # pivoted_stock_data = kwargs['task_instance'].xcom_pull(task_ids='preprocessing_df')
    pivoted_stock_data = relationship()
    
    try:
        conn = mysql_connection()
        
        SQL_NET = '''
        INSERT INTO network (dailydate, center, ind1, corr1, ind2, corr2, ind3, corr3, ind4, corr4, ind5, corr5) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        '''
        
        df = pd.DataFrame(pivoted_stock_data)

        # 'Industry_Sector' 열을 인덱스로 설정
        df.set_index('Industry_Sector', inplace=True)

        # 데이터프레임을 딕셔너리로 변환 (섹터명을 키로 사용)
        sector_dict = df.T.to_dict()
        # 결과 출력
        for sector, returns in sector_dict.items():
            print(f"{sector}: {returns}")

        for n100_industry in nasdaq100_industries:
            center_industry = n100_industry
            center_industry_returns = df.loc[center_industry]

            correlations = {}
            for industry in df.index:
                if industry != center_industry:
                    industry_return = df.loc[industry]
                    combined_df = pd.concat([center_industry_returns, industry_return], axis=1)
                    combined_df.columns = ['Center_Industry', 'Industry_Return']
                    correlation = combined_df['Center_Industry'].corr(combined_df['Industry_Return'])
                    correlations[industry] = correlation
            top_correlations = {k: correlations[k] for k in sorted(correlations, key=correlations.get, reverse=True)[:5]}
            keys = list(top_correlations.keys())
            values = list(top_correlations.values())
        
            insert_data(conn,SQL_NET, today, n100_industry, keys[0], values[0], keys[1], values[1], keys[2], values[2], keys[3], values[3], keys[4], values[4])
    except pymysql.err.IntegrityError as e:
        raise e
    
    finally:
        if conn:
            conn.close()
    print("성공")