from airflow.hooks.base import BaseHook
import boto3
import requests
from bs4 import BeautifulSoup
import pymysql
from datetime import datetime, timedelta
import pandas as pd
import google.generativeai as genai
import yfinance as yf
from airflow.models import Variable

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

industries = {'MSFT': 'Software - Infrastructure / Technology', 'AAPL': 'Consumer Electronics / Technology', 'NVDA': 'Semiconductors / Technology', 'GOOG': 'Internet Content & Information / Communication Services', 'GOOGL': 'Internet Content & Information / Communication Services', 'AMZN': 'Internet Retail / Consumer Cyclical', 'META': 'Internet Content & Information / Communication Services', 'AVGO': 'Semiconductors / Technology', 'TSLA': 'Auto Manufacturers / Consumer Cyclical', 'ASML': 'Semiconductor Equipment & Materials / Technology', 'COST': 'Discount Stores / Consumer Defensive', 'PEP': 'Beverages - Non-Alcoholic / Consumer Defensive', 'NFLX': 'Entertainment / Communication Services', 'AZN': 'Drug Manufacturers - General / Healthcare', 'AMD': 'Semiconductors / Technology', 'LIN': 'Specialty Chemicals / Basic Materials', 'ADBE': 'Software - Infrastructure / Technology', 'TMUS': 'Telecom Services / Communication Services', 'CSCO': 'Communication Equipment / Technology', 'QCOM': 'Semiconductors / Technology', 'INTU': 'Software - Application / Technology', 'PDD': 'Internet Retail / Consumer Cyclical', 'AMAT': 'Semiconductor Equipment & Materials / Technology', 'TXN': 'Semiconductors / Technology', 'CMCSA': 'Telecom Services / Communication Services', 'AMGN': 'Drug Manufacturers - General / Healthcare', 'ISRG': 'Medical Instruments & Supplies / Healthcare', 'INTC': 'Semiconductors / Technology', 'HON': 'Conglomerates / Industrials', 'MU': 'Semiconductors / Technology', 'BKNG': 'Travel Services / Consumer Cyclical', 'LRCX': 'Semiconductor Equipment & Materials / Technology', 'VRTX': 'Biotechnology / Healthcare', 'ADP': 'Staffing & Employment Services / Industrials', 'REGN': 'Biotechnology / Healthcare', 'ABNB': 'Travel Services / Consumer Cyclical', 'ADI': 'Semiconductors / Technology', 'MDLZ': 'Confectioners / Consumer Defensive', 'PANW': 'Software - Infrastructure / Technology', 'KLAC': 'Semiconductor Equipment & Materials / Technology', 'SBUX': 'Restaurants / Consumer Cyclical', 'GILD': 'Drug Manufacturers - General / Healthcare', 'SNPS': 'Software - Infrastructure / Technology', 'CDNS': 'Software - Application / Technology', 'MELI': 'Internet Retail / Consumer Cyclical', 'CRWD': 'Software - Infrastructure / Technology', 'PYPL': 'Credit Services / Financial Services', 'MAR': 'Lodging / Consumer Cyclical', 'CTAS': 'Specialty Business Services / Industrials', 'CSX': 'Railroads / Industrials', 'WDAY': 'Software - Application / Technology', 'NXPI': 'Semiconductors / Technology', 'ORLY': 'Specialty Retail / Consumer Cyclical', 'CEG': 'Utilities - Renewable / Utilities', 'PCAR': 'Farm & Heavy Construction Machinery / Industrials', 'MNST': 'Beverages - Non-Alcoholic / Consumer Defensive', 'MRVL': 'Semiconductors / Technology', 'ROP': 'Software - Application / Technology', 'CPRT': 'Specialty Business Services / Industrials', 'DASH': 'Internet Content & Information / Communication Services', 'DXCM': 'Medical Devices / Healthcare', 'FTNT': 'Software - Infrastructure / Technology', 'MCHP': 'Semiconductors / Technology', 'AEP': 'Utilities - Regulated Electric / Utilities', 'KDP': 'Beverages - Non-Alcoholic / Consumer Defensive', 'ADSK': 'Software - Application / Technology', 'TEAM': 'Software - Application / Technology', 'LULU': 'Apparel Retail / Consumer Cyclical', 'KHC': 'Packaged Foods / Consumer Defensive', 'PAYX': 'Staffing & Employment Services / Industrials', 'ROST': 'Apparel Retail / Consumer Cyclical', 'MRNA': 'Biotechnology / Healthcare', 'DDOG': 'Software - Application / Technology', 'TTD': 'Software - Application / Technology', 'ODFL': 'Trucking / Industrials', 'FAST': 'Industrial Distribution / Industrials', 'IDXX': 'Diagnostics & Research / Healthcare', 'EXC': 'Utilities - Regulated Electric / Utilities', 'CHTR': 'Telecom Services / Communication Services', 'CSGP': 'Real Estate Services / Real Estate', 'GEHC': 'Health Information Services / Healthcare', 'FANG': 'Oil & Gas E&P / Energy', 'EA': 'Electronic Gaming & Multimedia / Communication Services', 'VRSK': 'Consulting Services / Industrials', 'CCEP': 'Beverages - Non-Alcoholic / Consumer Defensive', 'CTSH': 'Information Technology Services / Technology', 'BKR': 'Oil & Gas Equipment & Services / Energy', 'BIIB': 'Drug Manufacturers - General / Healthcare', 'XEL': 'Utilities - Regulated Electric / Utilities', 'ON': 'Semiconductors / Technology', 'CDW': 'Information Technology Services / Technology', 'ANSS': 'Software - Application / Technology', 'MDB': 'Software - Infrastructure / Technology', 'DLTR': 'Discount Stores / Consumer Defensive', 'ZS': 'Software - Infrastructure / Technology', 'GFS': 'Semiconductors / Technology', 'TTWO': 'Electronic Gaming & Multimedia / Communication Services', 'ILMN': 'Diagnostics & Research / Healthcare', 'WBD': 'Entertainment / Communication Services', 'WBA': 'Pharmaceutical Retailers / Healthcare', 'SIRI': 'Entertainment / Communication Services'}


GEM_API_KEY = Variable.get('gem_api_key')
BUCKET_NAME = Variable.get('bucket_name')


# Gemini 모델 로드
genai.configure(api_key=GEM_API_KEY)
genai.GenerationConfig(max_output_tokens=180)
MODEL = genai.GenerativeModel('gemini-pro')


# S3 함수 선언
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
        # 파일 존재 여부 확인
        response = client.list_objects_v2(Bucket=bucket_name, Prefix=file_name)
        if 'Contents' in response:
            print(f"{file_name} already exists in {bucket_name}")
            return

        client.put_object(Bucket=bucket_name, Key=file_name, Body=bytes(article, 'utf-8'))
        print(f"Successfully uploaded {file_name} to {bucket_name}")
    
    except Exception as e:
        print(f"Failed to upload {file_name} to {bucket_name}: {e}")
        raise
    
    # try:
    #     client.put_object(Bucket=bucket_name, Key=file_name, Body=bytes(article, 'utf-8'))
    #     print(f"Successfully uploaded {file_name} to {bucket_name}")
    # except Exception as e:
    #     print(f"Failed to upload {file_name} to {bucket_name}: {e}")
    #     raise


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


# 뉴스 크롤링 함수들

# investing.com 뉴스 목록에 있는 뉴스들 url 수집
## url 접속 후 기사 작성 시간 확인하기 위함
def get_urls(ticker):
    urls = []
    for i in range(1, 3):
        url = f"https://www.investing.com/equities/{companies[ticker]}-news/{i}"
        
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        articles = soup.select('li[class="border-b border-[#E6E9EB] first:border-t last:border-0"]')
        
        for article in articles:
            pro = article.select_one('svg[height="17.5"]')
            if not pro:
                title_element = article.select_one('a[data-test="article-title-link"]')
                href = title_element.get('href')
                link = "http://www.investing.com" + href
                urls.append(link)
                
    print(f"{ticker}의 뉴스기사 {len(urls)}개를 확인합니다.")
    return urls


# 기사 작성시간 리턴
def get_written_time(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    wtime = soup.select('div[class="flex flex-col gap-2 text-warren-gray-700 md:flex-row md:items-center md:gap-0"] div span')
    if not wtime:
        return None
    wtime = wtime[0].text[10:]
    if wtime[-2:] == 'AM':
        year = wtime[6:10]
        month = wtime[:2]
        day = wtime[3:5]
        hour = wtime[12:14]
        minute = wtime[15:17]
        wtime = datetime.strptime(f"{year}-{month}-{day} {hour}:{minute}", "%Y-%m-%d %H:%M")
    else:
        year = wtime[6:10]
        month = wtime[:2]
        day = wtime[3:5]
        if int(wtime[12:14]) == 12:
            hour = wtime[12:14]
        else:
            hour = str(int(wtime[12:14]) + 12)
        minute = wtime[15:17]
        wtime = datetime.strptime(f"{year}-{month}-{day} {hour}:{minute}", "%Y-%m-%d %H:%M")
    return wtime


# 기사 원문 크롤링하는 함수
def get_article(wtime, url, ticker, s3_client):
    print(f"{wtime}에 작성된 기사를 긁어옵니다.")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # article
    # 'div[id="article"]' 아래의 모든 p 태그를 찾음
    all_p_tags = soup.select('div[id="article"] p')
    
     # 'blockquote' 태그 내의 p 태그를 찾음
    blockquote_p_tags = soup.select('div[id="article"] blockquote p')
    
    # 'blockquote' 태그 내의 p 태그를 제외한 p 태그를 필터링
    filtered_p_tags = [p for p in all_p_tags if p not in blockquote_p_tags]
    
    article = "\n".join([text.text for text in filtered_p_tags if text.name != 'span'])
    
    ### S3에 뉴스기사 원문 저장
    ymd = str(wtime)[:10]
    upload_to_s3(s3_client, article, BUCKET_NAME,
                 f"news/article/{ticker}/year={ymd[:4]}/month={ymd[5:7]}/day={ymd[8:10]}/{wtime}.txt")
    return article


# 뉴스 요약 함수
def summarize_article(wtime, ticker, article, s3_client):
    prompt = f"""
    I would like you to summarize the provided news article about {ticker} in a concise and objective way, mainly focusing on the impact on {ticker}'s stock.
    
    Followings are rules you must follow when generating an answer.
    
    1. If article includes advertisement such as "InvestingPro", it must be excluded from the summary.
    2. Do NOT start with an opening sentence, just give me the answer right away.
    3. The answer MUST be in Korean.
    4. When translating into Korean, you must end each sentence with period(.).
    5. The final Korean translated summary MUST NOT EXCEED 5 sentences.

    article: 
    {article}
    """
    try:
        summary = MODEL.generate_content(prompt).text
        
        ymd = str(wtime)[:10]
        file_name = f"news/summary/{ticker}/year={ymd[:4]}/month={ymd[5:7]}/day={ymd[8:10]}/{wtime}_sum.txt"
        upload_to_s3(s3_client, summary, BUCKET_NAME, file_name)
        
        print(f"Summary: {summary}")
        return file_name
    
    except Exception as e:
        print(f"Failed to summarize article: {e}")
        return "오류 발생"


# yfinance api로 주요 재무지표 받아오는 함수
# name, industry, market_cap(시가총액), per, psr, pbr, ev/ebitda
def return_indicators(ticker):
    
    nasdaq = yf.Ticker(ticker).info
    
    name = nasdaq["shortName"]
    industry = f'{nasdaq["industry"]}/{nasdaq["sector"]}'
    industry = industry.replace(" & ","-")
    industry = industry.replace("—", " - ")
    
    market_cap = nasdaq["marketCap"]
    
    try:
        per = round(nasdaq["trailingPE"], 2)
    except:
        per = 0
    
    try:
        psr = round(nasdaq["priceToSalesTrailing12Months"], 2)
    except:
        psr = 0

    try:
        pbr = round(nasdaq["priceToBook"], 2)
    except:
        pbr = 0

    try:
        ev_ebitda = round(nasdaq["enterpriseToEbitda"], 2)
    except:
        ev_ebitda = 0
        
    try:
        close_price = nasdaq["previousClose"]
    except:
        close_price = 0
        
    tick = yf.Ticker(ticker)
    hist = tick.history(period="1mo")[-2:]
    prev = hist.iloc[0]["Close"]
    cur = hist.iloc[1]["Close"]
    fluc = round((cur - prev) / prev * 100, 2)

    return name, industry, market_cap, per, psr, pbr, ev_ebitda, fluc, close_price


# 실행 함수
def execute(tickers):
    s3_client = s3_connection()
    conn = mysql_connection()
    
    for ticker in tickers:
        urls = get_urls(ticker)
        summaries = []
        count = 0
        today = datetime.now().strftime("%Y-%m-%d")
        
        for idx, url in enumerate(urls):
            wtime = get_written_time(url)
            if wtime is not None:
                year = today[:4]
                month = today[5:7]
                day = today[8:10]

                crawling_time = datetime.strptime(f"{year}-{month}-{day} 5:00", "%Y-%m-%d %H:%M")

                if crawling_time - timedelta(days=1) <= wtime <= crawling_time:
                    count += 1
                    article = get_article(wtime, url, ticker, s3_client)
                    # s3 적재
                    summary = summarize_article(wtime, ticker, article, s3_client)
                    summaries.append(summary)
                    
                else:
                    continue
            else:
                continue

        # SQL 구문 작성
        SQL1_INSERT ='''
        INSERT INTO daily_update (dailydate, ticker, name, industry, news_summary, market_cap, per, psr, pbr, ev_ebitda, fluc, close_price) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        '''

        SQL1_UPDATE = '''
        UPDATE daily_update
        SET name = %s, industry = %s, news_summary = %s, market_cap = %s, per = %s, psr = %s, pbr = %s, ev_ebitda = %s, fluc = %s, close_price = %s
        WHERE dailydate = %s AND ticker = %s
        '''
        # 기사가 없는 경우
        if count == 0:
            date = today
            
            summary = "None"
            
            name, industry, market_cap, per, psr, pbr, ev_ebitda, fluc, close_price = return_indicators(ticker)

            df = pd.DataFrame({"date": [date], "ticker": [ticker], "name": [name], "industry": [industry], "summary": [summary],
                               "market_cap": [market_cap], "per": [per], "psr": [psr], "pbr": [pbr], "ev_ebitda": [ev_ebitda], "fluc":[fluc], "close_price":[close_price]})
            
            # date 열을 datetime 형식으로 변환
            df["date"] = pd.to_datetime(df["date"])
            
            # 주말에 해당하는 행 삭제
            # df = df[~df["date"].dt.dayofweek.isin([5, 6])]
            
            # if df.empty:
            #     print(f"{ticker} 주말 데이터는 제외합니다.")
            #     continue
            
            # DB에 데이터가 이미 존재하는지 여부
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM daily_update WHERE dailydate = %s AND ticker = %s", (date, ticker))
                    result = cursor.fetchone()
            
                    if result[0] == 0:
                        cursor.execute(SQL1_INSERT, (df["date"][0].strftime("%Y-%m-%d"), ticker, name, industry, summary, market_cap, per, psr, pbr, ev_ebitda, fluc, close_price))
                    else:
                        cursor.execute(SQL1_UPDATE, (name, industry, summary, market_cap, per, psr, pbr, ev_ebitda, fluc, close_price, df["date"][0].strftime("%Y-%m-%d"), ticker))
                    
                    conn.commit()
                    print(f"{ticker} insert/update 완료")

            except Exception as e:
                print(f"Failed to insert/update data for {ticker}: {e}")
                conn.rollback()
        
        # 기사가 있는경우
        else:
            date = today
            
            name, industry, market_cap, per, psr, pbr, ev_ebitda, fluc, close_price = return_indicators(ticker)

            for summary in summaries:
                df = pd.DataFrame({"date": [date], "ticker": [ticker], "name": [name], "industry": [industry], "summary": [summary],
                                   "market_cap": [market_cap], "per": [per], "psr": [psr], "pbr": [pbr], "ev_ebitda": [ev_ebitda], "fluc":[fluc], "close_price":[close_price]})
                
                # date 열을 datetime 형식으로 변환
                df["date"] = pd.to_datetime(df["date"])
                
                # 주말에 해당하는 행 삭제
                # df = df[~df["date"].dt.dayofweek.isin([5, 6])]
                
                # if df.empty:
                #     print(f"{ticker} 주말 데이터는 제외합니다.")
                #     continue
                
                try:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT COUNT(*) FROM daily_update WHERE dailydate = %s AND ticker = %s", (date, ticker))
                        result = cursor.fetchone()
                        
                        if result[0] == 0:
                            cursor.execute(SQL1_INSERT, (df["date"][0].strftime("%Y-%m-%d"), ticker, name, industry, summary, market_cap, per, psr, pbr, ev_ebitda, close_price))
                        else:
                            cursor.execute(SQL1_UPDATE, (name, industry, summary, market_cap, per, psr, pbr, ev_ebitda, close_price, df["date"][0].strftime("%Y-%m-%d"), ticker))
                        
                        conn.commit()
                        print(f"{ticker} insert/update 완료")
                
                except Exception as e:
                    print(f"Failed to insert/update data for {ticker}: {e}")
                    conn.rollback()
                
                print(f"{ticker} DB에 저장합니다.")
    
    conn.close()
