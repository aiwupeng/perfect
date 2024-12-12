# coding=utf-8
import akshare as ak
import pandas as pd
stock_lrb_em_df = ak.stock_lrb_em(date="20221231")  # 获取利润表数据
lrb = stock_lrb_em_df[stock_lrb_em_df['股票代码'].isin(['601668','601186','601800'])].drop('序号',axis=1).set_index('股票代码')

stock_zcfz_em_df = ak.stock_zcfz_em(date="20221231")  # 获取资产负债表数据
zcfz = stock_zcfz_em_df[stock_zcfz_em_df['股票代码'].isin(['601668','601186','601800'])].drop('序号',axis=1).set_index('股票代码')
financial_data = pd.concat([lrb, zcfz], axis=1)

stock_financial_report_sina_df = ak.stock_financial_report_sina(stock="600004", symbol="现金流量表")


financial_data['营业利润率'] = (financial_data['营业总收入'] - financial_data['营业总支出-营业支出']) / financial_data['营业总收入']
financial_data['资本收益率'] = financial_data['净利润'] / financial_data['股东权益合计']