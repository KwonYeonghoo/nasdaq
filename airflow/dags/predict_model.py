import pandas as pd
import numpy as np

import FinanceDataReader as fdr

from sklearn.preprocessing import MinMaxScaler

import pymysql
from keras.models import Sequential
from keras.layers import Dense, LSTM

# For time stamps
from datetime import datetime, timedelta
from airflow.hooks.base import BaseHook

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

def insert_data(conn, SQL, val_list):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.executemany(SQL, val_list)
    conn.commit()

com = ['MSFT','AAPL','NVDA','GOOG','GOOGL','AMZN','META','AVGO','TSLA','ASML','COST','PEP','NFLX','AZN','AMD','LIN','ADBE','TMUS',
 'CSCO','QCOM','INTU','PDD','AMAT','TXN','CMCSA','AMGN','ISRG','INTC','HON','MU','BKNG','LRCX','VRTX','ADP','REGN','ABNB','ADI','MDLZ',
 'PANW','KLAC','SBUX','GILD','SNPS','CDNS','MELI','CRWD','PYPL','MAR','CTAS','CSX','WDAY','NXPI','ORLY','CEG','PCAR','MNST','MRVL','ROP',
 'CPRT','DASH','DXCM','FTNT','MCHP','AEP','KDP','ADSK','TEAM','LULU','KHC','PAYX','ROST','MRNA','DDOG','TTD','ODFL','FAST','IDXX','EXC',
 'CHTR','CSGP','GEHC','FANG','EA','VRSK','CCEP','CTSH','BKR','BIIB','XEL','ON','CDW','ANSS','MDB','DLTR','ZS','GFS','TTWO','ILMN','WBD',
 'WBA','SIRI']

def predict_stock_prices(com):
    result = pd.DataFrame(columns=['Date', 'Company', 'Prediction','compare_rate'])

    # 데이터 수집& 예측
    for j in range(len(com)):
        print(com[j],j)
        
        df = fdr.DataReader(com[j])   # 나스닥 100 기업 데이터 가져오기
        
        # 데이터 로드 확인(나중에 빼기)
        if df.empty:
            raise ValueError(f"Data for {com[j]} could not be loaded.")
        
        data = df.filter(['Open'])    # Open 가격만 사용
        dataset = data.values
        training_data_len = int(np.ceil( len(dataset) * .90 ))  # 데이터 90%를 학습용 데이터로 사용
        
        # 데이터 스케일링
        scaler = MinMaxScaler(feature_range=(0,1))  #데이터를 0과 1 사이로 스케일
        scaled_data = scaler.fit_transform(dataset)
        
        
        # 학습 데이터 준비
        train_data = scaled_data[0:int(training_data_len), :]

        # LSTM 입/출력으로 사용
        x_train = []
        y_train = []

        for i in range(60, len(train_data)):
            x_train.append(train_data[i-60:i, 0])
            y_train.append(train_data[i, 0])
            if i <= 61:
                print()

        x_train, y_train = np.array(x_train), np.array(y_train)
        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

        # 모델 정의 및 컴파일
        model = Sequential()
        model.add(LSTM(128, return_sequences=True, input_shape=(x_train.shape[1], 1)))
        model.add(LSTM(64, return_sequences=False))
        model.add(Dense(25))
        model.add(Dense(1))

        model.compile(optimizer='adam', loss='mean_squared_error')
        
        model.load_weights(f"/home/ubuntu/data/save_weights/stock_{com[j]}.h5")
        
        # 테스트 데이터 준비 및 예측
        test_data = scaled_data[-60:, :]
        
        x_test = []
        x_test.append(test_data[-60:, 0])
        x_test = np.array(x_test)
        x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
        
        predictions = [] 
        
        # 다음 5일 동안의 주가 예측
        for i in range(5):
            pred = model.predict(x_test)
            predictions.append(pred[0][0])
            x_test = np.append(x_test[:, 1:, :], [[pred[0]]], axis=1)
                
        # 예측값 원래 값(스케일링 이전)으로 변환
        predictions = np.array(predictions).reshape(-1, 1)
        predictions = scaler.inverse_transform(predictions)
        
        # 예측 결과 result(DataFrame)에 저장
        # result.loc[len(result)] = [datetime.strptime(datetime.today().strftime("%Y-%m-%d"),"%Y-%m-%d")+ timedelta(days=5), com[j], predictions[4][0],0]
        result.loc[len(result)] = [(datetime.today() + timedelta(days=5)).strftime("%Y-%m-%d"), com[j], predictions[4][0],0]
        
    val_list = result.values.tolist() # DataFrame의 값을 리스트로 변환하여 반환 # values: DF의 모든 값 -> numpy 배열로 반환/ tolist() 메서드: numpy 배열 -> 파이썬 리스트로 변환 Why? DB(SQL)에 여러 행을 삽입할 때 사용하기 위함
    return val_list


def save_predict_stockprice_to_db(**kwargs):
    val_list = kwargs['task_instance'].xcom_pull(task_ids='predict_stock_prices')
    
    conn = mysql_connection()
    
    SQL_PRED_INSERT = '''INSERT INTO predict_price (dailydate,ticker,price,compare_rate) values (%s,%s,%s,%s);'''
    
    SQL_PRED_UPDATE = '''
    UPDATE predict_price
    SET price = %s, compare_rate = %s
    WHERE dailydate = %s AND ticker = %s;
    '''
    
    with conn.cursor() as cursor:
        try:
            insert_data(conn,SQL_PRED_INSERT, val_list)
        except pymysql.err.IntegrityError as e:
            if e.args[0] == 1062:   
                cursor.executemany(SQL_PRED_UPDATE, val_list)          
                conn.commit()
            else:
                raise e
    conn.close()
    print("성공")