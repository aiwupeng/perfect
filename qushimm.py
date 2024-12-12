# coding=utf-8
import pandas as pd
import pandas_datareader as pdr
from datetime import datetime
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import yfinance as yf

# 获取股票数据
def get_stock_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    return data

# 数据清洗
def clean_data(data):
    data.dropna(inplace=True)  # 去除缺失值
    return data

# 计算特征
def calculate_features(data):
    data['SMA_50'] = data['Close'].rolling(window=50).mean()
    data['SMA_200'] = data['Close'].rolling(window=200).mean()
    data['SMA_80'] = data['Close'].rolling(window=80).mean()  # 添加SMA_80的计算
    # 计算RSI指标
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    return data

# 构建模型
def build_model(data):
    X = data[['SMA_50', 'SMA_200', 'RSI']]
    y = (data['Close'].shift(-1) > data['Close']).astype(int)  # 下一天股价是否上涨
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    return model

# 策略回测
def backtest(model, data):
    last_prices = data['Close'].shift(1)
    predictions = model.predict(data[['SMA_50', 'SMA_200', 'RSI']])
    data['Prediction'] = predictions
    data['Signal'] = np.where(predictions == 1, 'Buy', 'Sell')
    # 这里需要添加实际的回测逻辑，比如计算策略收益等
    return data

# 主程序
if __name__ == "__main__":
    ticker = 'AAPL'
    start_date = datetime(2010, 1, 1)
    end_date = datetime(2020, 1, 1)
    data = get_stock_data(ticker, start_date, end_date)
    data = clean_data(data)
    data = calculate_features(data)
    model = build_model(data)
    result = backtest(model, data)
    print(result.tail())