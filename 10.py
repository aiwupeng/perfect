# coding=utf-8
import streamlit as st
import baostock as bs
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

# 设置全局中文字体和负号显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def get_stock_data(ticker, start_date, end_date):
    """
    获取股票的历史数据。
    """
    lg = bs.login()
    rs = bs.query_history_k_data_plus("sh." + ticker,
                                      "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                                      start_date=start_date, end_date=end_date, frequency="d", adjustflag="3")
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    bs.logout()

    # 确保日期列存在并设置为索引
    if 'date' in result.columns:
        result['date'] = pd.to_datetime(result['date'])
        result.set_index('date', inplace=True)
    else:
        st.error("数据中缺少日期列")
        return pd.DataFrame()

    # 确保收盘价列存在
    if 'close' not in result.columns:
        st.error("数据中缺少收盘价列")
        return pd.DataFrame()

    return result

def generate_trading_signals(stock_data, short_window, long_window):
    """
    生成买卖信号。
    """
    if 'close' not in stock_data.columns:
        st.error("数据中缺少收盘价列")
        return pd.DataFrame()

    stock_data['短期均线'] = stock_data['close'].rolling(window=short_window).mean()
    stock_data['长期均线'] = stock_data['close'].rolling(window=long_window).mean()
    stock_data['信号'] = 0
    stock_data['信号'][stock_data['短期均线'] > stock_data['长期均线']] = 1  # 买入信号
    stock_data['信号'][stock_data['短期均线'] < stock_data['长期均线']] = -1  # 卖出信号
    return stock_data

def plot_trading_signals(stock_data):
    """
    绘制买卖信号图。
    """
    if '短期均线' not in stock_data.columns or '长期均线' not in stock_data.columns or '信号' not in stock_data.columns:
        st.error("数据中缺少均线或信号列")
        return

    plt.figure(figsize=(10, 6))
    plt.plot(stock_data.index, stock_data['close'], label='收盘价')
    plt.plot(stock_data.index, stock_data['短期均线'], label='短期均线')
    plt.plot(stock_data.index, stock_data['长期均线'], label='长期均线')
    plt.scatter(stock_data[stock_data['信号'] == 1].index, stock_data[stock_data['信号'] == 1]['close'], color='green', label='买入信号')
    plt.scatter(stock_data[stock_data['信号'] == -1].index, stock_data[stock_data['信号'] == -1]['close'], color='red', label='卖出信号')
    plt.xlabel('日期')
    plt.ylabel('价格')
    plt.title('股票买卖点')
    plt.legend()
    st.pyplot(plt)

def main():
    st.title('个股买卖点分析')

    symbol = st.text_input('请输入股票代码', '600000')
    start_date = st.text_input('请输入开始日期', '2024-01-01')
    end_date = st.text_input('请输入结束日期', '2024-11-08')

    try:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
    except ValueError:
        st.error("日期格式不正确，请输入格式为 YYYY-MM-DD 的日期")
        return
    else:
        if st.button('分析买卖点'):
            stock_data = get_stock_data(symbol, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

            if stock_data.empty:
                st.error("未获取到数据，请检查股票代码和日期范围")
                return

            st.write("数据列名:", stock_data.columns.tolist())

            stock_data_with_signals = generate_trading_signals(stock_data, short_window=20, long_window=60)
            plot_trading_signals(stock_data_with_signals)

if __name__ == "__main__":
    main()