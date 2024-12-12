# coding=utf-8
import akshare as ak
import backtrader as bt

# 初始化AKShare数据源
akshare = ak.AKShare()
# 使用AKShare数据源查询特定股票（由 "stock_code" 参数指定）在指定日期范围内的数据
df = akshare.query(symbols=["stock_code"], start_date='20200131', end_date='20230228')

# 定义交易策略：如果当前没有持有该股票，则买入股票，并设置止盈点位
def buy_with_stop_loss(ctx: bt.ExecContext):
    pos = ctx.getposition()
    if not pos.size:
        # 计算目标股票数量，根据 "percent" 参数确定应购买的股票数量
        ctx.buy_shares = ctx.get_cash() * 0.1  # 假设购买可用资金的10%
        ctx.hold_bars = 100
    else:
        ctx.close()  # 如果持有，则卖出

# 创建策略配置，初始资金为500000
my_config = bt.StrategyConfig(initial_cash=500000)
# 使用配置、数据源、起始日期、结束日期，以及刚才定义的交易策略创建策略对象
strategy = bt.Strategy(data=df, config=my_config)
# 添加执行策略，设置股票代码和要执行的函数
strategy.add_execution(fn=buy_with_stop_loss, symbols=["stock_code"])
# 执行回测，并打印出回测结果的度量值（四舍五入到小数点后四位）
result = strategy.run()
print(result.metrics_df.round(4))