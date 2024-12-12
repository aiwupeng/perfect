# coding=utf-8
import pandas as pd
def indicator_score(stkcd):
    data = pd.read_excel('data\\16_23_full.xlsx')
# 策略：营业收入15分、毛利率10分、核心利润率10分，获现率15分，有息负债率10分，造血功能10分、
# 研发10分 # 经营资产周转率10分，经营资产报酬率10，
#成长能力
    data['成长'] = data['Growth'].apply(
            lambda y: 12 + min(round((y - 0.2) / 0.05), 3) if y >= 0.2 else 10 + max(round((y - 0.2) / 0.05), -10))
        # 毛利率打分
    data['竞争'] = data['Xgross'].apply(
            lambda y: 5 + min(round(y / 0.1), 5) if y >= 0 else 5 + max(round(y / 0.1), -5))

            # 核心利润率打分
    data['潜力'] = data['Xcore_sales'].apply(
                lambda y: 5 + min(round(y / 0.1), 5) if y >= 0 else 5 + max(round(y / 0.1), -5))

            # 获现率打分
    data['获现'] = data['Cfo_core'].apply(
                lambda y: 10 + min(round((y - 1) / 0.1), 5) if y >= 1 else 10 + max(round((y - 1) / 0.1), -10))
            # 有息负债率打分
    data['风险'] = data['Finance_debt'].apply(
                lambda y: 7 + min(round((0.3 - y) / 0.1), 3) if y <= 0.3 else 5 + max(round((0.3 - y) / 0.1), -5))

            # 造血打分
    data['造血'] =data['H_ability'].apply(
                lambda y: 5 + min(round((y - 0.5) / 0.05), 5) if y >= 0.5 else 5 + max(round((y - 0.5) / 0.05), -5))

            # 研发打分
    data['研发'] = data['Xrd'].apply(
                lambda y: 5 + min(round(y / 0.05), 5) if y >= 0 else 5 + max(round(y / 0.05), -5))

            # 经营资产周转率打分
    data['周转率'] = data['Xtat'].apply(
                lambda y: 5 + min(round(y / 0.1), 5) if y >= 0 else 5 + max(round(y / 0.1), -5))
            # 经营资产报酬率打分
    data['报酬率'] = data['XOroa'].apply(
                lambda y: 5 + min(round(y / 0.1), 5) if y >= 0 else 5 + max(round(y / 0.1), -5))
          # 计算总得分
    data['总分'] = data[['成长', '竞争', '潜力', '获现', '风险', '造血', '研发', '周转率', '报酬率']].sum(axis=1)
    return data[['Stkcd', 'Name', 'Year', 'IndName','Yret', '成长', '竞争', '潜力', '获现', '风险', '造血', '研发', '周转率',
                 '报酬率', '总分']]
df=indicator_score('Stkcd')
df.to_excel('data\\scores_new.xlsx',index=False)
df_601=df[df['总分']>=60]
#df_601=df_60[df_60['收入']>=8]
df_601.to_excel('data\\60_new.xlsx', index=False)

groupby_df=df_601.groupby("Stkcd")["Year"].nunique().reset_index()
df_602=groupby_df[groupby_df["Year"]>=5].rename(columns={'Year':'fre'})
total=pd.merge(df_601,df_602,on="Stkcd")
total.to_excel('data\\niubi05.xlsx', index=False)