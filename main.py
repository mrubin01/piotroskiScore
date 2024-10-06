import sys
import numpy as np
import pandas as pd
import warnings
import csv
import yfinance as yf
import metrics
import functions

warnings.filterwarnings('ignore')
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

"""
STEPS
Step 1: call the function get_fundamentals to download the data for the three statements and check whether
        it contains four years, ["2023", "2022", "2021", "2020"]

CHECK TICKERS IN Alpaca_Positions.xsl: only 3 show a score, the other fails

"""

# Step 1

# uncomment the lines below to create a ticker list from a txt file
# my_file = open("active_tickers.txt", "r")
# data = my_file.read()
# data_into_list = data.replace('\n', ', ').split(", ")
# ticker_list = list(filter(None, data_into_list))

ticker_list = ["AAPL", "MSFT", "GOOGL", "TSLA"]
ticker_to_use = ticker_list[3]


if functions.get_fundamentals(ticker_to_use)[0]:
    inc_stat = functions.get_fundamentals(ticker_to_use)[1]
    balance_sheet = functions.get_fundamentals(ticker_to_use)[2]
    cash_flow = functions.get_fundamentals(ticker_to_use)[3]
else:  # no data for the ticker or missing years
    sys.exit()


# net_income_2023 = inc_stat["2023"]["Net Income"]
# total_assets_2023 = balance_sheet["2023"]["Total Assets"]
# oper_cashflow_2023 = cash_flow["2023"]["Operating Cash Flow"]
# long_term_debt_2023 = balance_sheet["2023"]["Long Term Debt"]
# current_assets_2023 = balance_sheet["2023"]["Current Assets"]
# current_liabilities_2023 = balance_sheet["2023"]["Current Liabilities"]
# shares_issued_2023 = balance_sheet["2023"]["Share Issued"]
# gross_profit_2023 = inc_stat["2023"]["Gross Profit"]
# total_revenue_2023 = inc_stat["2023"]["Total Revenue"]


if functions.get_fundamentals(ticker_to_use)[4] == "2023":
    avg_total_asset = (balance_sheet["2023"]["Total Assets"] + balance_sheet["2022"]["Total Assets"] \
                      + balance_sheet["2021"]["Total Assets"] + balance_sheet["2020"]["Total Assets"]) / 4

    df_data = {
        "Ticker": [ticker_to_use],
        "Net Income": int(inc_stat["2023"]["Net Income"]),
        "Return On Assets CY": float(int(inc_stat["2023"]["Net Income"]) / avg_total_asset),
        "Return On Assets PY": float(int(inc_stat["2022"]["Net Income"]) / avg_total_asset),
        "Oper Cash Flow": int(cash_flow["2023"]["Operating Cash Flow"]),
        "Oper Cash Flow vs Net Income": int(cash_flow["2023"]["Operating Cash Flow"]) - int(inc_stat["2023"]["Net Income"]),
        "Leverage CY - PY": balance_sheet["2023"]["Long Term Debt"] - balance_sheet["2022"]["Long Term Debt"],
        "Current Ratio CY": float(balance_sheet["2023"]["Current Assets"] / balance_sheet["2023"]["Current Liabilities"]),
        "Current Ratio PY": float(balance_sheet["2022"]["Current Assets"] / balance_sheet["2022"]["Current Liabilities"]),
        "Shares Issued CY": int(balance_sheet["2023"]["Share Issued"]),
        "Shares Issued PY": int(balance_sheet["2022"]["Share Issued"]),
        "Gross margin CY": float(inc_stat["2023"]["Gross Profit"] / inc_stat["2023"]["Total Revenue"]),
        "Gross margin PY": float(inc_stat["2022"]["Gross Profit"] / inc_stat["2022"]["Total Revenue"]),
        "Asset Turnover CY": float(inc_stat["2023"]["Total Revenue"] / balance_sheet["2023"]["Total Assets"]),
        "Asset Turnover PY": float(inc_stat["2022"]["Total Revenue"] / balance_sheet["2022"]["Total Assets"])
    }

elif functions.get_fundamentals(ticker_to_use)[4] == "2024":
    avg_total_asset = (balance_sheet["2024"]["Total Assets"] + balance_sheet["2023"]["Total Assets"] \
                      + balance_sheet["2022"]["Total Assets"] + balance_sheet["2021"]["Total Assets"]) / 4

    df_data = {
        "Ticker": [ticker_to_use],
        "Net Income": int(inc_stat["2024"]["Net Income"]),
        "Return On Assets CY": float(int(inc_stat["2024"]["Net Income"]) / avg_total_asset),
        "Return On Assets PY": float(int(inc_stat["2023"]["Net Income"]) / avg_total_asset),
        "Oper Cash Flow": int(cash_flow["2024"]["Operating Cash Flow"]),
        "Oper Cash Flow vs Net Income": int(cash_flow["2024"]["Operating Cash Flow"]) - int(inc_stat["2024"]["Net Income"]),
        "Leverage CY - PY": balance_sheet["2024"]["Long Term Debt"] - balance_sheet["2023"]["Long Term Debt"],
        "Current Ratio CY": float(balance_sheet["2024"]["Current Assets"] / balance_sheet["2024"]["Current Liabilities"]),
        "Current Ratio PY": float(balance_sheet["2023"]["Current Assets"] / balance_sheet["2023"]["Current Liabilities"]),
        "Shares Issued CY": int(balance_sheet["2024"]["Share Issued"]),
        "Shares Issued PY": int(balance_sheet["2023"]["Share Issued"]),
        "Gross margin CY": float(inc_stat["2024"]["Gross Profit"] / inc_stat["2024"]["Total Revenue"]),
        "Gross margin PY": float(inc_stat["2023"]["Gross Profit"] / inc_stat["2023"]["Total Revenue"]),
        "Asset Turnover CY": float(inc_stat["2024"]["Total Revenue"] / balance_sheet["2024"]["Total Assets"]),
        "Asset Turnover PY": float(inc_stat["2023"]["Total Revenue"] / balance_sheet["2023"]["Total Assets"])
    }

columns_to_delete = ["Net Income", "Return On Assets CY", "Return On Assets PY", "Oper Cash Flow", \
                     "Oper Cash Flow vs Net Income", "Leverage CY - PY", "Current Ratio CY", "Current Ratio PY", \
                     "Shares Issued CY", "Shares Issued PY", "Gross margin CY", "Gross margin PY", \
                     "Asset Turnover CY", "Asset Turnover PY"]

df = pd.DataFrame(df_data)

df["Positive Net Income"] = [1 if x > 0 else 0 for x in df["Net Income"]]
df["Positive Return On Assets"] = np.where(df["Return On Assets CY"] > df["Return On Assets PY"], 1, 0)
df["Positive Oper Cash Flow"] = np.where(df["Oper Cash Flow"] > 0, 1, 0)
df["Oper Cash Flow higher than Net Income"] = np.where(df["Oper Cash Flow vs Net Income"] > 0, 1, 0)
df["Decrease in Leverage"] = [1 if x < 0 else 0 for x in df["Leverage CY - PY"]]
df["Increase in Current Ratio"] = np.where(df["Current Ratio CY"] > df["Current Ratio PY"], 1, 0)
df["No Shares Issued"] = np.where(df["Shares Issued CY"] <= df["Shares Issued PY"], 1, 0)
df["Increase in Gross Margin"] = np.where(df["Gross margin CY"] > df["Gross margin PY"], 1, 0)
df["Increase in Asset Turnover"] = np.where(df["Asset Turnover CY"] > df["Asset Turnover PY"], 1, 0)
df["Piotroski Score"] = df["Positive Net Income"] + df["Positive Return On Assets"] + df["Positive Oper Cash Flow"] \
    + df["Oper Cash Flow higher than Net Income"] + df["Decrease in Leverage"] + df["Increase in Current Ratio"] \
    + df["No Shares Issued"] + df["Increase in Gross Margin"] + df["Increase in Asset Turnover"]

df.drop(columns=columns_to_delete, inplace=True)

piotroski_score = df._get_value(0, "Piotroski Score")
pos_net_income = df._get_value(0, "Positive Net Income")
pos_roa = df._get_value(0, "Positive Return On Assets")
pos_oper_cashflow = df._get_value(0, "Positive Oper Cash Flow")
oper_cashflow_vs_net_income = df._get_value(0, "Oper Cash Flow higher than Net Income")
decrease_leverage = df._get_value(0, "Decrease in Leverage")
increase_current_ratio = df._get_value(0, "Increase in Current Ratio")
no_shares_issued = df._get_value(0, "No Shares Issued")
increase_gross_margin = df._get_value(0, "Increase in Gross Margin")
increase_asset_turnover = df._get_value(0, "Increase in Asset Turnover")

print("\n" + ticker_to_use)
print("PIOTROSKI SCORE: " + str(piotroski_score))
print("Positive Net Income: " + str(pos_net_income))
print("Positive ROA: " + str(pos_roa))
print("Positive Cash Flow: " + str(pos_oper_cashflow))
print("Cash Flow vs Net Income: " + str(oper_cashflow_vs_net_income))
print("Decrease Leverage: " + str(decrease_leverage))
print("Increased Current Ratio: " + str(increase_current_ratio))
print("No shares issued: " + str(no_shares_issued))
print("Increase Gross Margin: " + str(increase_gross_margin))
print("Increase Asset Turnover: " + str(increase_asset_turnover) + "\n")


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


if __name__ == '__main__':
    print_hi('PyCharm')
