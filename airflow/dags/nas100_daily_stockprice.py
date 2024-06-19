import warnings
warnings.filterwarnings(action='ignore')
# import FinanceDataReader as fdr
import pymysql
import pandas as pd
from datetime import datetime, timedelta
from airflow.hooks.base import BaseHook
import yfinance as yf
import time

# 나스닥 100 기업 명단
companies = {
    'MSFT': 'microsoft-corp',
    'AAPL': 'apple-computer-inc',
    'NVDA': 'nvidia-corp',
    'GOOG': 'google-inc-c',
    'GOOGL': 'google-inc',
    'AMZN': 'amazon-com-inc',
    'META': 'facebook-inc',
    'AVGO': 'avago-technologies',
    'TSLA': 'tesla-motors',
    'ASML': 'asml-holdings',
    'COST': 'costco-whsl-corp-new',
    'PEP': 'pepsico',
    'NFLX': 'netflix,-inc.',
    'AZN': 'astrazeneca-plc-ads',
    'AMD': 'adv-micro-device',
    'LIN': 'linde-plc',
    'ADBE': 'adobe-sys-inc',
    'TMUS': 'metropcs-communications',
    'CSCO': 'cisco-sys-inc',
    'QCOM': 'qualcomm-inc',
    'INTU': 'intuit',
    'PDD': 'pinduoduo',
    'AMAT': 'applied-matls-inc',
    'TXN': 'texas-instru',
    'CMCSA': 'comcast-corp-new',
    'AMGN': 'amgen-inc',
    'ISRG': 'intuitive-surgical-inc',
    'INTC': 'intel-corp',
    'HON': 'honeywell-intl',
    'MU': 'micron-tech',
    'BKNG': 'priceline.com-inc',
    'LRCX': 'lam-research-corp',
    'VRTX': 'vertex-pharm',
    'ADP': 'auto-data-process',
    'REGN': 'regeneron-phar.',
    'ABNB': 'airbnb-inc',
    'ADI': 'analog-devices',
    'MDLZ': 'mondelez-international-inc',
    'PANW': 'palo-alto-netwrk',
    'KLAC': 'kla-tencor-corp',
    'SBUX': 'starbucks-corp',
    'GILD': 'gilead-sciences-inc',
    'SNPS': 'synopsys-inc',
    'CDNS': 'cadence-design-system-inc',
    'MELI': 'mercadolibre',
    'CRWD': 'crowdstrike-holdings-inc',
    'PYPL': 'paypal-holdings-inc',
    'MAR': 'marriott-intl',
    'CTAS': 'cintas-corp',
    'CSX': 'csx-corp',
    'WDAY': 'workday-inc',
    'NXPI': 'nxp-semiconductors',
    'ORLY': 'oreilly-automotive',
    'CEG': 'constellation-energy',
    'PCAR': 'paccar-inc',
    'MNST': 'monster-beverage',
    'MRVL': 'marvell-technology-group-ltd',
    'ROP': 'roper-industries',
    'CPRT': 'copart-inc',
    'DASH': 'doordash-inc',
    'DXCM': 'dexcom',
    'FTNT': 'fortinet',
    'MCHP': 'microchip-technology-inc',
    'AEP': 'american-electric',
    'KDP': 'dr-pepper-snapple',
    'ADSK': 'autodesk-inc',
    'TEAM': 'atlassian-corp-plc',
    'LULU': 'lululemon-athletica',
    'KHC': 'kraft-foods-inc',
    'PAYX': 'paychex-inc',
    'ROST': 'ross-stores-inc',
    'MRNA': 'moderna',
    'DDOG': 'datadog-inc',
    'TTD': 'trade-desk-inc',
    'ODFL': 'old-dominion-freight-line-inc',
    'FAST': 'fastenal-co',
    'IDXX': 'idexx-laboratorie',
    'EXC': 'exelon-corp',
    'CHTR': 'charter-communications',
    'CSGP': 'costar-group',
    'GEHC': 'ge-healthcare-holding-llc',
    'FANG': 'diamondback-energy-inc',
    'EA': 'electronic-arts-inc',
    'VRSK': 'verisk-analytics-inc',
    'CCEP': 'coca-cola-ent',
    'CTSH': 'cognizant-technology-solutio',
    'BKR': 'baker-hughes',
    'BIIB': 'biogen-idec-inc',
    'XEL': 'xcel-energy',
    'ON': 'on-semiconductor',
    'CDW': 'cdw-corp',
    'ANSS': 'ansys',
    'MDB': 'mongodb',
    'DLTR': 'dollar-tree-inc',
    'ZS': 'zscaler-inc',
    'GFS': 'globalfoundries',
    'TTWO': 'take-two-interactive',
    'ILMN': 'illumina,-inc.',
    'WBD': 'discovery-holding-co',
    'WBA': 'walgreen-co',
    'SIRI': 'sirius-satellite-radio-inc'
}


def read_stock_data(ticker, current_date):
    tick = yf.Ticker(ticker)
    df = tick.history(period="2y")
    
    if 'Close' not in df.columns:
        raise KeyError(f"DataFrame does not contain 'Close' column for ticker {ticker}")

    df = df.reset_index()
    df = df[["Date", "Open", "High", "Low", "Close"]]
    df = df.assign(Ticker=ticker, axis=0)
    df['ma20'] = df['Close'].rolling(window=20).mean()
    df['std'] = df['Close'].rolling(window=20).std()
    df['upper'] = df['ma20'] + (df['std'] * 2)
    df['lower'] = df['ma20'] - (df['std'] * 2)
    df = df.fillna(value="None")
    df_ohlc = df[['Ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'ma20', 'std', 'upper', 'lower']]
    df_ohlc['Date'] = pd.to_datetime(df_ohlc['Date'])
    df_ohlc['Date'] = df_ohlc['Date'].astype('int64') // 10**6
    return df_ohlc


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

def insert_data(tickers):
    conn = mysql_connection()
    today = datetime.now().strftime("%Y-%m-%d")

    # SQL 구문 작성
    SQL7_INSERT = '''
    INSERT INTO stock_data (ticker, date, open_price, high_price, low_price, close_price, ma20, std, upper, lower)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    
    try:
        with conn.cursor() as cursor:
            for ticker in tickers:
                df_ohlc = read_stock_data(ticker, today)
                
                # 데이터베이스가 비어 있는지 확인
                cursor.execute("SELECT COUNT(*) FROM stock_data WHERE ticker = %s", (ticker,))
                result = cursor.fetchone()
                
                # 데이터베이스가 비어 있는 경우 데이터프레임의 모든 행을 insert
                if result[0] == 0:
                    for index, row in df_ohlc.iterrows():
                        
                        try:
                            cursor.execute(SQL7_INSERT, (row['Ticker'], row['Date'], row['Open'], row['High'], row['Low'],
                                                        row['Close'], row['ma20'], row['std'], row['upper'], row['lower']))
                        except pymysql.err.IntegrityError as e:
                            raise e
                            
                # 데이터(해당 종목)가 있는 경우 마지막 행만 insert
                else:
                    last_row = df_ohlc.iloc[-1]
                    try:
                        cursor.execute(SQL7_INSERT, (last_row['Ticker'], last_row['Date'], last_row['Open'], last_row['High'],
                                                    last_row['Low'], last_row['Close'], last_row['ma20'], last_row['std'],
                                                    last_row['upper'], last_row['lower']))
                    except pymysql.err.IntegrityError as e:
                        raise e
                
                print(f"{ticker} insert/update 완료")
            
                time.sleep(2)
                
            conn.commit()
    
    except Exception as e:
        print(f"Failed to insert/update data: {e}")
        conn.rollback()
    
    finally:
        conn.close()