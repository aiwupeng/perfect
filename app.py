# coding=utf-8
import streamlit as st
import pandas as pd
import akshare as ak
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

# 设置全局中文字体
font_path = "path_to_font/SimHei.ttf"  # 请确保替换为实际的字体路径
font_prop = FontProperties(fname=font_path)
plt.rcParams['axes.unicode_minus'] = False


# 数据加载函数
def load_data():
    file = st.file_uploader("上传数据文件", type=["xlsx"])
    if file is not None:
        df = pd.read_excel(file)
        return df
    return pd.DataFrame()


# 评分逻辑提取成函数
def score_growth(growth):
    if growth >= 0.2:
        return 12 + min(round((growth - 0.2) / 0.05), 3)
    else:
        return 10 + max(round((growth - 0.2) / 0.05), -10)


def score_gross(gross):
    return 5 + min(round(gross / 0.1), 5) if gross >= 0 else 5 + max(round(gross / 0.1), -5)


def score_core_sales(core_sales):
    return 5 + min(round(core_sales / 0.1), 5) if core_sales >= 0 else 5 + max(round(core_sales / 0.1), -5)


def score_cfo(cfo):
    return 10 + min(round((cfo - 1) / 0.1), 5) if cfo >= 1 else 10 + max(round((cfo - 1) / 0.1), -10)


def score_finance_debt(debt):
    return 7 + min(round((0.3 - debt) / 0.1), 3) if debt <= 0.3 else 5 + max(round((0.3 - debt) / 0.1), -5)


# 计算公司评分
def scoring_system(df, stock_cd):
    filtered_data = df[df['Stkcd'].astype(int) == int(stock_cd)]
    if not filtered_data.empty:
        # 使用评分函数
        filtered_data['成长'] = filtered_data['Growth'].apply(score_growth)
        filtered_data['竞争'] = filtered_data['Xgross'].apply(score_gross)
        filtered_data['核心利润率'] = filtered_data['Xcore_sales'].apply(score_core_sales)
        filtered_data['获现能力'] = filtered_data['Cfo_core'].apply(score_cfo)
        filtered_data['风险'] = filtered_data['Finance_debt'].apply(score_finance_debt)
        filtered_data['总分'] = filtered_data[['成长', '竞争', '核心利润率', '获现能力', '风险']].sum(axis=1)

        return filtered_data[['Stkcd', 'Name', 'Year', '总分']]
    return pd.DataFrame()


# 可视化函数
def visualization(stkcd_data):
    charts = [
        ('Other_income', '政府补贴'),
        ('Growth', '成长能力'),
        ('Gross', '竞争能力'),
        ('Core_sales', '核心利润率'),
        ('Cfo_core', '获现能力'),
        ('Finance_debt', '风险表现'),
    ]
    cols = st.columns(3)
    for i, (col, title) in enumerate(charts):
        with cols[i % 3]:
            fig, ax = plt.subplots()
            ax.plot(stkcd_data['Year'], stkcd_data[col], label=col, color='red', linewidth=3)
            ax.set_title(title)
            ax.set_xlabel('年份')
            ax.set_ylabel('金额/百分比')
            ax.legend()
            st.pyplot(fig)


# 资金流向查询函数
def fund_flow_query(stock_code, market):
    try:
        stock_individual_fund_flow_df = ak.stock_individual_fund_flow(stock=stock_code, market=market)
        return stock_individual_fund_flow_df
    except Exception as e:
        st.error(f'查询失败：{e}')
        return None


# 十大流通股东持仓情况查询函数
def get_top_ten_free_holders(stock_code, date):
    try:
        all_holders_df = ak.stock_gdfx_free_holding_analyse_em(date=date)
        specific_stock_holders_df = all_holders_df[all_holders_df['股票代码'] == stock_code]
        return specific_stock_holders_df
    except Exception as e:
        st.error(f"获取数据时发生错误：{e}")
        return pd.DataFrame()


def main():
    st.title("彭博士公司评分系统")
    df = load_data()

    if df.empty:
        st.warning("请上传数据文件")
        return

    # 公司评分部分
    stock_cd = st.text_input("公司代码:", '002139')
    if st.button('计算评分'):
        scored_data = scoring_system(df, stock_cd)
        if not scored_data.empty:
            st.write("评分结果：")
            st.dataframe(scored_data)
        else:
            st.error("没有找到对应的公司数据。")

    # 图表生成部分
    stkcd_data = df[df['Stkcd'].astype(int) == int(stock_cd)]
    if st.button('生成图表'):
        visualization(stkcd_data)

    # 竞争地位展示
    st.title("竞争地位:")
    columns_to_display1 = stkcd_data[
        ['Name', 'IndName', 'Year', 'Gross_profit', 'Gross', 'P_RD', 'Oper_revenue', 'Growth']]
    st.dataframe(columns_to_display1)

    # 暴雷分析
    st.title("暴雷分析:")
    columns_to_display2 = stkcd_data[
        ['Name', 'IndName', 'Year', 'Non_current_asset_sum', 'Receivable_sales', 'P_other_receivable', 'Inventory',
         'Core_income']]
    st.dataframe(columns_to_display2)

    # 资产利润脱节分析
    st.title("资产利润脱节分析:")
    columns_to_display3 = stkcd_data[
        ['Name', 'IndName', 'Year', 'P_operating_assets', 'Oper_revenue', 'Core_income', 'Core_sales', 'Cfo',
         'Cfo_core']]
    st.dataframe(columns_to_display3)

    # 现金流分析
    st.title("现金流分析:")
    columns_to_display4 = stkcd_data[
        ['Name', 'IndName', 'Year', 'Cfo_core', 'Cfo', 'Buy_cash', 'Invest_cash', 'Free_cash']]
    st.dataframe(columns_to_display4)

    # 个股资金流向数据查询
    st.title('个股资金流向数据查询')
    stock_code = st.text_input('输入股票代码', '002139')
    market_type = st.selectbox('选择市场类型', ('上海证券交易所', '深圳证券交易所'), index=0)
    market = 'sh' if market_type == '上海证券交易所' else 'sz'
    if st.button('查询资金流向'):
        fund_flow_df = fund_flow_query(stock_code, market)
        if fund_flow_df is not None:
            st.write('查询结果：')
            st.dataframe(fund_flow_df)

    # 个股十大流通股东持仓情况
    st.title('个股十大流通股东持仓情况')
    stock_code = st.text_input('请输入股票代码', '002139')  # 默认输入股票代码
    date = st.date_input('请选择财报发布季度最后日', value=None)
    if st.button('获取数据'):
        if stock_code and date:
            result_df = get_top_ten_free_holders(stock_code, date.strftime('%Y%m%d'))
            st.write("个股十大流通股东持仓情况：")
            st.dataframe(result_df)
        else:
            st.error("请输入有效的股票代码和日期")


if __name__ == "__main__":
    main()
