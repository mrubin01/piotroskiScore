import pandas as pd
import yfinance as yf
import numpy as np

stock_data = yf.Ticker("CLCO")
inc_stat = stock_data.income_stmt
balance_sheet = stock_data.balance_sheet
cash_flow = stock_data.cashflow

print(str(pd.to_datetime(inc_stat.columns[0]).year))
print(str(pd.to_datetime(balance_sheet.columns[0]).year))
print(str(pd.to_datetime(cash_flow.columns[0]).year))
#
print(len(inc_stat.columns))
print(len(balance_sheet.columns))
print(len(cash_flow.columns))
