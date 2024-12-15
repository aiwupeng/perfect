# coding=utf-8
import streamlit as st
import pandas as pd
import akshare as ak
import matplotlib.pyplot as plt
import os
from matplotlib.font_manager import FontProperties

# 设置全局中文字体和负号显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def load_data():
    #mainDir = st.secrets["MAIN_DIR"]  # 确保在Streamlit的秘密中设置了MAIN_DIR
    filePath = os.path.join("data/16_23_full.xlsx")
    df = pd.read_excel(filePath)
    return df
def scoring_system(df, stock_cd):
    filtered_data = df[df['Stkcd'].astype(int) == int(stock_cd)]
    if not filtered_data.empty:
        # 评分逻辑...
        # 营业收入增长率打分
        filtered_data['成长'] = filtered_data['Growth'].apply(
                lambda y: 12 + min(round((y - 0.2) / 0.05), 3) if y >= 0.2 else 10 + max(round((y - 0.2) / 0.05), -10))
            # 毛利率打分
        filtered_data['竞争'] = filtered_data['Xgross'].apply(
                lambda y: 5 + min(round(y / 0.1), 5) if y >= 0 else 5 + max(round(y / 0.1), -5))
            # 核心利润率打分
        filtered_data['潜力'] = filtered_data['Xcore_sales'].apply(
                lambda y: 5 + min(round(y / 0.1), 5) if y >= 0 else 5 + max(round(y / 0.1), -5))
            # 获现率打分
        filtered_data['获现'] = filtered_data['Cfo_core'].apply(
                lambda y: 10 + min(round((y - 1) / 0.1), 5) if y >= 1 else 10 + max(round((y - 1) / 0.1), -10))
            # 有息负债率打分
        filtered_data['风险'] = filtered_data['Finance_debt'].apply(
                lambda y: 7 + min(round((0.3 - y) / 0.1), 3) if y <= 0.3 else 5 + max(round((0.3 - y) / 0.1), -5))
            # 造血打分
        filtered_data['造血'] = filtered_data['H_ability'].apply(
                lambda y: 5 + min(round((y - 0.5) / 0.05), 5) if y >= 0.5 else 5 + max(round((y - 0.5) / 0.05), -5))
            # 研发打分
        filtered_data['研发'] = filtered_data['Xrd'].apply(
                lambda y: 5 + min(round(y / 0.05), 5) if y >= 0 else 5 + max(round(y / 0.05), -5))
            # 经营资产周转率打分
        filtered_data['周转率'] = filtered_data['Xtat'].apply(
                lambda y: 5 + min(round(y / 0.1), 5) if y >= 0 else 5 + max(round(y / 0.1), -5))
            # 经营资产报酬率打分
        filtered_data['报酬率'] = filtered_data['XOroa'].apply(
                lambda y: 5 + min(round(y / 0.1), 5) if y >= 0 else 5 + max(round(y / 0.1), -5))
            # 计算总得分
        filtered_data['总分'] = filtered_data[
                ['成长', '竞争', '潜力', '获现', '风险', '造血', '研发', '周转率', '报酬率']].sum(axis=1)
        return filtered_data[
                ['Stkcd', 'Name', 'Year', 'IndName','Yret', '成长', '竞争', '潜力', '获现', '风险', '造血', '研发', '周转率',
                 '报酬率', '总分']]
    else:
        return pd.DataFrame()

def visualization(stkcd_data):
    # 可视化逻辑...
    charts = [
        ('Other_income', '政府补贴'),
        ('Growth', '成长能力'),
        ('Gross', '竞争能力'),
        ('Core_sales', '核心利润率'),
        ('Cfo_core', '获现能力'),
        ('Finance_debt', '风险表现'),
        ('H_ability', '造血能力'),
        ('P_RD', '研发支出'),
        ('Operating_assets_tat', '经营资产周转率'),
        ('Operating_assets_roa', '经营资产报酬率'),
        ('Finance_assets_roa', '金融资产报酬率'),
        ('Roe', '净资产收益率'),
    ]
    cols = st.columns(3)
    for i, (col, title) in enumerate(charts):
        with cols[i % 3]:
            fig, ax = plt.subplots()
            ax.plot(stkcd_data['Year'], stkcd_data[col], label=col, color='red', linewidth=3)
            if f'{col}_mean' in stkcd_data.columns:
                ax.plot(stkcd_data['Year'], stkcd_data[f'{col}_mean'], label=f'{col}中值', linestyle='--', color='green',
                        linewidth=3)
            ax.set_title(title)
            ax.set_xlabel('年份')
            ax.set_ylabel('金额/百分比')
            ax.legend()
            # 绘图逻辑...
            st.pyplot(fig)
def fund_flow_query(stock_code, market):
    try:
        stock_individual_fund_flow_df = ak.stock_individual_fund_flow(stock=stock_code, market=market)
        return stock_individual_fund_flow_df
    except Exception as e:
        st.error(f'查询失败：{e}')
        return None
def get_top_ten_free_holders(stock_code, date):
    """
    获取指定股票和日期的十大流通股东持仓情况。
    参数：
    stock_code (str): 股票代码。
    date (str): 财报发布季度最后日，格式为YYYYMMDD。
    返回：
    pd.DataFrame: 十大流通股东持仓情况的数据框。
    """
    try:
        # 使用AKShare获取所有股票的十大流通股东数据
        all_holders_df = ak.stock_gdfx_free_holding_analyse_em(date=date)

        # 筛选出特定股票的十大流通股东数据
        specific_stock_holders_df = all_holders_df[all_holders_df['股票代码'] == stock_code]

        return specific_stock_holders_df
    except Exception as e:
        st.error(f"获取数据时发生错误：{e}")
        return pd.DataFrame()

def main():
    st.title("彭博士公司评分系统")
    df = load_data()
    stock_cd = st.text_input("请输入公司代码:",'')
     
    if st.button('计算评分'):
        scored_data = scoring_system(df, stock_cd)
        if not scored_data.empty:
            st.write("评分结果：")
            st.dataframe(scored_data)
        else:
            st.error("没有找到对应的公司数据。")
    stkcd_data = df[df['Stkcd'].astype(int) == int(stock_cd)]
    if st.button('生成图表'):
        visualization(stkcd_data)
    st.title("竞争地位:")
    columns_to_display1 = stkcd_data[
            ['Name', 'IndName', 'Year', 'Gross_profit', 'Gross', 'P_RD', 'Oper_revenue', 'Growth']]
    st.dataframe(columns_to_display1)
    st.title("暴雷分析:")
    columns_to_display2 = stkcd_data[
            ['Name', 'IndName', 'Year', 'Non_current_asset_sum', 'Receivable_sales', 'P_other_receivable', 'Inventory', 'Core_income',
             'Other_income', 'Non_income', 'Exp_income', 'Admin_income', 'Finance_income']]
    st.dataframe(columns_to_display2)
    st.title("资产利润脱节分析:")
    columns_to_display3 = stkcd_data[
            ['Name', 'IndName', 'Year', 'P_operating_assets', 'Oper_revenue', 'Core_income', 'Core_sales', 'Cfo', 'Cfo_core',
             'Operating_assets_tat', 'Operating_assets_roa', 'P_finance_assets', 'Non_income', 'Finance_assets_roa', 'G_inventory',
             'DFix_assets']]
    st.dataframe(columns_to_display3)
    st.title("现金流分析:")
    columns_to_display4 = stkcd_data[
            ['Name', 'IndName', 'Year', 'Cfo_core', 'Cfo', 'Buy_cash', 'Invest_cash', 'Free_cash',
             'Excess_cash', 'Finance_cash_in', 'Oper_revenue']]
    st.dataframe(columns_to_display4)
    st.title('个股资金流向数据查询')
    stock_code = st.text_input('输入股票代码', '002139')
    market_type = st.selectbox('选择市场类型', ('上海证券交易所', '深圳证券交易所'), index=0)
    market = 'sh' if market_type == '上海证券交易所' else 'sz'
    if st.button('查询资金流向'):
        fund_flow_df = fund_flow_query(stock_code, market)
        if fund_flow_df is not None:
            st.write('查询结果：')
            st.dataframe(fund_flow_df)

    # 页面标题
    st.title('个股十大流通股东持仓情况')
    # 创建一个文本输入框，让用户输入股票代码
    stock_code = st.text_input('请输入股票代码', '002139')  # 以贵州茅台为例，默认输入600519
    # 创建一个日期选择器，让用户选择财报发布季度最后日
    date = st.date_input('请选择财报发布季度最后日', value=None)
    # 检查输入是否有效，并获取数据
    if st.button('获取数据'):
        if stock_code and date:
            # 调用函数获取数据
            result_df = get_top_ten_free_holders(stock_code, date.strftime('%Y%m%d'))
            # 展示数据
            st.write("个股十大流通股东持仓情况：")
            st.dataframe(result_df)
        else:
            st.error("请输入有效的股票代码和日期")


if __name__ == "__main__":
    main()
