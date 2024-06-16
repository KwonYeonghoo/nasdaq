import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import FinanceDataReader as fdr

from sklearn.preprocessing import MinMaxScaler

import pymysql
from keras.models import Sequential
from keras.layers import Dense, LSTM

# For time stamps
from datetime import datetime


tickers = ['MSFT','AAPL','NVDA','GOOG','GOOGL','AMZN','META','AVGO','TSLA','ASML','COST','PEP','NFLX','AZN','AMD','LIN','ADBE','TMUS',
 'CSCO','QCOM','INTU','PDD','AMAT','TXN','CMCSA','AMGN','ISRG','INTC','HON','MU','BKNG','LRCX','VRTX','ADP','REGN','ABNB','ADI','MDLZ',
 'PANW','KLAC','SBUX','GILD','SNPS','CDNS','MELI','CRWD','PYPL','MAR','CTAS','CSX','WDAY','NXPI','ORLY','CEG','PCAR','MNST','MRVL','ROP',
 'CPRT','DASH','DXCM','FTNT','MCHP','AEP','KDP','ADSK','TEAM','LULU','KHC','PAYX','ROST','MRNA','DDOG','TTD','ODFL','FAST','IDXX','EXC',
 'CHTR','CSGP','GEHC','FANG','EA','VRSK','CCEP','CTSH','BKR','BIIB','XEL','ON','CDW','ANSS','MDB','DLTR','ZS','GFS','TTWO','ILMN','WBD',
 'WBA','SIRI']

result = pd.DataFrame(columns=['Date', 'Company', 'Prediction','compare_rate'])

for j in range(len(tickers)):
    print(tickers[j],j)
    df = fdr.DataReader(tickers[j])
    data = df.filter(['Open'])
    dataset = data.values
    training_data_len = int(np.ceil( len(dataset) * .90 ))
    
    scaler = MinMaxScaler(feature_range=(0,1))
    scaled_data = scaler.fit_transform(dataset)
    
    train_data = scaled_data[0:int(training_data_len), :]

    x_train = []
    y_train = []

    for i in range(60, len(train_data)):
        x_train.append(train_data[i-60:i, 0])
        y_train.append(train_data[i, 0])
        if i <= 61:
            print()

    x_train, y_train = np.array(x_train), np.array(y_train)
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

    model = Sequential()
    model.add(LSTM(128, return_sequences=True, input_shape=(x_train.shape[1], 1)))
    model.add(LSTM(64, return_sequences=False))
    model.add(Dense(25))
    model.add(Dense(1))

    model.compile(optimizer='adam', loss='mean_squared_error')
    model.load_weights(f"save_weights/stock_{tickers[j]}.h5")
    
    test_data = scaled_data[-60:, :]
    
    x_test = []
    x_test.append(test_data[-60:, 0])

    x_test = np.array(x_test)
    

    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
    
    for i in range(5):
        pred = model.predict(x_test)
        predictions.append(pred[0][0])
        x_test = np.append(x_test[:, 1:, :], [[pred[0]]], axis=1)
            

    predictions = np.array(predictions).reshape(-1, 1)
    predictions = scaler.inverse_transform(predictions)
    
    result.loc[len(result)] = [datetime.datetime.strptime(datetime.datetime.today().strftime("%Y-%m-%d"),"%Y-%m-%d")+datetime.timedelta(days=5), tickers[j], predictions[4][0],0]
    
val_list = result.values.tolist()
    

print("--------sql저장---------")
sql = "insert into  predict_price (dailydate,ticker,price,compare_rate) values (%s,%s,%s,%s)"
with pymysql.connect(host='nasdaq-db.clcgk04eeism.ap-northeast-2.rds.amazonaws.com',user='admin',password='admin1234',db='nasdaq',charset='utf8') as conn:
    with conn.cursor() as cursor:
        cursor.executemany(sql,val_list) ## 중첩 리스트를 전달 
        
        conn.commit()

