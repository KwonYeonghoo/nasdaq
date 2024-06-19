import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import pymysql
from airflow.hooks.base import BaseHook

markets = ['commodities', 'world-indices', 'currencies', 'bonds']

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

def scrape_data(markets):
    all_data = pd.DataFrame()

    for market in markets:
        url = f'https://finance.yahoo.com/{market}'
        print(f"Scraping data for market: {market}")
        valuation_measures, market_code = scrape_valuation_measures(url)
        if valuation_measures:
            df = pd.DataFrame(valuation_measures[1:], columns=valuation_measures[0])

            df['Title'] = market_code   # 시장 종류 
            df['Scraping Date'] = datetime.now().strftime("%Y-%m-%d") # 날짜

            # 필요한 컬럼만 선택
            select_col = ['Scraping Date', 'Name', 'Title', 'Last Price', 'Change', '% Change']
            
            df = df[select_col]

            df.reset_index(drop=True, inplace=True) 
            all_data = pd.concat([all_data, df], ignore_index=True) # 합치기
        
        else:
            print(f"Failed to scrape data for market: {market}")

    insert_data_into_db(all_data)

def scrape_valuation_measures(url):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    header = {
        "user-agent":user_agent,
        "my-name": "Hoo"
        }
    response = requests.get(url, headers=header)
    
    if response.status_code == 200:          
        soup = BeautifulSoup(response.content, 'html.parser')
            
        valuation_table = soup.find('table')

        table_data = []
        for row in valuation_table.find_all(['tr']):
            row_data = [cell.get_text(strip=True) for cell in row.find_all(['th', 'td'])]
            table_data.append(row_data)

        market_code = soup.find('div', class_='Cur(p)', attrs={'data-test': 'watchlist-name'}).find('h1').text
        return table_data, market_code

    else:
        return None, None

def insert_data_into_db(df):
    conn = mysql_connection()

    # SQL 구문 작성
    SQL_MARKET_INSERT = """
    INSERT INTO nasdaq.daily_market (dt, market_name, market_title, market_close, market_change, per_change)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    SQL_MARKET_UPDATE = """
    UPDATE nasdaq.daily_market
    SET market_title = %s,
        market_close = %s,
        market_change = %s,
        per_change = %s
    WHERE dt = %s AND market_name = %s
    """
    
    try:
        with conn.cursor() as cursor:
            for _, row in df.iterrows():
                scraping_date = row['Scraping Date']
                name = row['Name']
                title = row['Title']
                try:
                    last_price = float(row['Last Price'].replace(',', '')) if row['Last Price'] else None
                except ValueError:
                    last_price = None
                try:
                    change = float(row['Change'].replace(',', '').replace('+', '').replace('%', '')) if row['Change'] else None
                except ValueError:
                    change = None
                try:
                    percent_change = float(row['% Change'].replace(',', '').replace('%', '')) if row['% Change'] else None
                except ValueError:
                    percent_change = None
               
                # 데이터가 있는지 확인
                cursor.execute("SELECT COUNT(*) FROM nasdaq.daily_market WHERE dt = %s AND market_name = %s", (scraping_date, name))
                result = cursor.fetchone()
                
                if result[0] == 0:
                    # 데이터가 없는 경우 INSERT
                    cursor.execute(SQL_MARKET_INSERT, (scraping_date, name, title, last_price, change, percent_change))
                else:
                    # 데이터가 있는 경우 UPDATE
                    cursor.execute(SQL_MARKET_UPDATE, (title, last_price, change, percent_change, scraping_date, name))

                print(f"{name} 데이터 처리 완료")
            
        conn.commit()
        print("모든 데이터 처리 완료")
        
    except Exception as e:
        print(f"데이터 처리 중 오류 발생: {e}")
        conn.rollback()
        
    finally:
        conn.close()

