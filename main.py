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
This code compute the Piotroski F-score from the stock's fundamental data. It is based on 9 metrics. Sometimes 
the data is missing, then the score will be based on fewer metrics. Only the stocks with 8/9 or 9/9 will 
be shown with all the details.

Piotroski F-score aim is to identify companies which are improving their financial position in performance. Three 
areas are assessed: Profitability, Leverage/Liquidity, Efficiency. A high score suggest strong financial 
conditions, while at the opposite, a low score can detect a firm's weaknesses.
 
STEPS
Step 1: call the function get_fundamentals to download the data for the three statements and check the last 
        available year and how many years are shown

Step 2: try to extract all the values needed to compute the metrics. Only Total Assets is calculated as an average
        of all the available years, while all the other values refer to the last available year (CY) and
        to the previous year (PY). The dictionary df_data will contain these values

Step 3: create a dataframe with the values in the dictionary df_data and based on them add 9 new calculated columns
        containing the metrics. These new columns can have only 3 values: 1, 0 or None. Drop all the columns 
        but one with the ticker name ("Ticker") and the 9 columns with the metrics. 

Step 4: the scores will be contained in the dictionary scores to compute the valid metrics and the positive values.
        If a stock has all valid metrics and six of them are positive the score will be 6/9; if the valid metrics
        are seven and the positive ones are only 4, the score will be 4/7.

Step 5: only the stocks with a score of 8/9 or 9/9 will be shown with the details.

"""

# Step 1

# uncomment the lines below to create a ticker list from a txt file
# my_file = open("active_tickers.txt", "r")
# data = my_file.read()
# data_into_list = data.replace('\n', ', ').split(", ")
# ticker_list = list(filter(None, data_into_list))

ticker_list = ["XOMO", "RYLD", "ASG", "CUBA", "BITO"]
ticker_to_use = ticker_list[4]

for ticker_to_use in ticker_list:

    # download data and split it into 3 variables: income statement, balance sheet and cash flow
    if functions.get_fundamentals(ticker_to_use)[0]:
        inc_stat = functions.get_fundamentals(ticker_to_use)[1]
        balance_sheet = functions.get_fundamentals(ticker_to_use)[2]
        cash_flow = functions.get_fundamentals(ticker_to_use)[3]
        last_year = functions.get_fundamentals(ticker_to_use)[4]
        years = functions.get_fundamentals(ticker_to_use)[5]
    else:  # no data for the ticker or missing years
        print("Missing data! Impossible to compute the metrics")
        sys.exit()

    # Step 2
    # check if the last year available is 2023 or 2024
    if last_year == "2023":
        # try to extract the values that will be used to compute the 9 metrics
        if years == 4:
            try:
                avg_total_asset = (balance_sheet["2023"]["Total Assets"] + balance_sheet["2022"]["Total Assets"] \
                                  + balance_sheet["2021"]["Total Assets"] + balance_sheet["2020"]["Total Assets"]) / years
            except Exception as e:
                avg_total_asset = None
        elif years == 3:
            try:
                avg_total_asset = (balance_sheet["2023"]["Total Assets"] + balance_sheet["2022"]["Total Assets"] \
                                  + balance_sheet["2021"]["Total Assets"]) / years
            except Exception as e:
                avg_total_asset = None
        elif years == 2:
            try:
                avg_total_asset = (balance_sheet["2023"]["Total Assets"] + balance_sheet["2022"]["Total Assets"]) / years
            except Exception as e:
                avg_total_asset = None

        try:
            net_income = int(inc_stat["2023"]["Net Income"])
        except Exception as e:
            net_income = None
        try:
            roa_cy = int(inc_stat["2023"]["Net Income"]) / avg_total_asset
        except Exception as e:
            roa_cy = None
        try:
            roa_py = int(inc_stat["2022"]["Net Income"]) / avg_total_asset
        except Exception as e:
            roa_py = None
        try:
            oper_cashflow = int(cash_flow["2023"]["Operating Cash Flow"])
        except Exception as e:
            oper_cashflow = None
        try:
            leverage_cy_py = balance_sheet["2023"]["Long Term Debt"] - balance_sheet["2022"]["Long Term Debt"]
        except Exception as e:
            leverage_cy_py = None
        try:
            current_ratio_cy = float(balance_sheet["2023"]["Current Assets"] / balance_sheet["2023"]["Current Liabilities"])
        except Exception as e:
            current_ratio_cy = None
        try:
            current_ratio_py = float(balance_sheet["2022"]["Current Assets"] / balance_sheet["2022"]["Current Liabilities"])
        except Exception as e:
            current_ratio_py = None
        try:
            shares_issued_cy = int(balance_sheet["2023"]["Share Issued"])
        except Exception as e:
            shares_issued_cy = None
        try:
            shares_issued_py = int(balance_sheet["2022"]["Share Issued"])
        except Exception as e:
            shares_issued_py = None
        try:
            gross_margin_cy = float(inc_stat["2023"]["Gross Profit"] / inc_stat["2023"]["Total Revenue"])
        except Exception as e:
            gross_margin_cy = None
        try:
            gross_margin_py = float(inc_stat["2022"]["Gross Profit"] / inc_stat["2022"]["Total Revenue"])
        except Exception as e:
            gross_margin_py = None
        try:
            asset_turnover_cy = float(inc_stat["2023"]["Total Revenue"] / balance_sheet["2023"]["Total Assets"])
        except Exception as e:
            asset_turnover_cy = None
        try:
            asset_turnover_py = float(inc_stat["2022"]["Total Revenue"] / balance_sheet["2022"]["Total Assets"])
        except Exception as e:
            asset_turnover_py = None

        # calculate here to avoid None type
        diff_cashflow_income = 0
        if oper_cashflow and net_income:
            diff_cashflow_income = oper_cashflow - net_income

        df_data = {
            "Ticker": [ticker_to_use],
            "Net Income": net_income,
            "Return On Assets CY": roa_cy,
            "Return On Assets PY": roa_py,
            "Oper Cash Flow": oper_cashflow,
            "Oper Cash Flow vs Net Income": diff_cashflow_income,
            "Leverage CY - PY": leverage_cy_py,
            "Current Ratio CY": current_ratio_cy,
            "Current Ratio PY": current_ratio_py,
            "Shares Issued CY": shares_issued_cy,
            "Shares Issued PY": shares_issued_py,
            "Gross margin CY": gross_margin_cy,
            "Gross margin PY": gross_margin_py,
            "Asset Turnover CY": asset_turnover_cy,
            "Asset Turnover PY": asset_turnover_py
        }

    elif functions.get_fundamentals(ticker_to_use)[4] == "2024":
        # try to extract the values that will be used to compute the 9 metrics
        if years == 4:
            try:
                avg_total_asset = (balance_sheet["2024"]["Total Assets"] + balance_sheet["2023"]["Total Assets"] \
                                  + balance_sheet["2022"]["Total Assets"] + balance_sheet["2021"]["Total Assets"]) / years
            except Exception as e:
                avg_total_asset = None
        elif years == 3:
            try:
                avg_total_asset = (balance_sheet["2024"]["Total Assets"] + balance_sheet["2023"]["Total Assets"] \
                                  + balance_sheet["2022"]["Total Assets"]) / years
            except Exception as e:
                avg_total_asset = None
        elif years == 2:
            try:
                avg_total_asset = (balance_sheet["2024"]["Total Assets"] + balance_sheet["2023"]["Total Assets"]) / years
            except Exception as e:
                avg_total_asset = None

        try:
            net_income = int(inc_stat["2024"]["Net Income"])
        except Exception as e:
            net_income = None
        try:
            roa_cy = int(inc_stat["2024"]["Net Income"]) / avg_total_asset
        except Exception as e:
            roa_cy = None
        try:
            roa_py = int(inc_stat["2023"]["Net Income"]) / avg_total_asset
        except Exception as e:
            roa_py = None
        try:
            oper_cashflow = int(cash_flow["2024"]["Operating Cash Flow"])
        except Exception as e:
            oper_cashflow = None
        try:
            leverage_cy_py = balance_sheet["2024"]["Long Term Debt"] - balance_sheet["2023"]["Long Term Debt"]
        except Exception as e:
            leverage_cy_py = None
        try:
            current_ratio_cy = float(balance_sheet["2024"]["Current Assets"] / balance_sheet["2024"]["Current Liabilities"])
        except Exception as e:
            current_ratio_cy = None
        try:
            current_ratio_py = float(balance_sheet["2023"]["Current Assets"] / balance_sheet["2023"]["Current Liabilities"])
        except Exception as e:
            current_ratio_py = None
        try:
            shares_issued_cy = int(balance_sheet["2024"]["Share Issued"])
        except Exception as e:
            shares_issued_cy = None
        try:
            shares_issued_py = int(balance_sheet["2023"]["Share Issued"])
        except Exception as e:
            shares_issued_py = None
        try:
            gross_margin_cy = float(inc_stat["2024"]["Gross Profit"] / inc_stat["2024"]["Total Revenue"])
        except Exception as e:
            gross_margin_cy = None
        try:
            gross_margin_py = float(inc_stat["2023"]["Gross Profit"] / inc_stat["2023"]["Total Revenue"])
        except Exception as e:
            gross_margin_py = None
        try:
            asset_turnover_cy = float(inc_stat["2024"]["Total Revenue"] / balance_sheet["2024"]["Total Assets"])
        except Exception as e:
            asset_turnover_cy = None
        try:
            asset_turnover_py = float(inc_stat["2023"]["Total Revenue"] / balance_sheet["2023"]["Total Assets"])
        except Exception as e:
            asset_turnover_py = None

        # calculate here to avoid None type
        diff_cashflow_income = None
        if oper_cashflow and net_income:
            diff_cashflow_income = oper_cashflow - net_income

        df_data = {
            "Ticker": [ticker_to_use],
            "Net Income": net_income,
            "Return On Assets CY": roa_cy,
            "Return On Assets PY": roa_py,
            "Oper Cash Flow": oper_cashflow,
            "Oper Cash Flow vs Net Income": diff_cashflow_income,
            "Leverage CY - PY": leverage_cy_py,
            "Current Ratio CY": current_ratio_cy,
            "Current Ratio PY": current_ratio_py,
            "Shares Issued CY": shares_issued_cy,
            "Shares Issued PY": shares_issued_py,
            "Gross margin CY": gross_margin_cy,
            "Gross margin PY": gross_margin_py,
            "Asset Turnover CY": asset_turnover_cy,
            "Asset Turnover PY": asset_turnover_py
        }
    else:
        print("Last year is neither 2023 nor 2024")

    # Step 3
    columns_to_delete = ["Net Income", "Return On Assets CY", "Return On Assets PY", "Oper Cash Flow", \
                         "Oper Cash Flow vs Net Income", "Leverage CY - PY", "Current Ratio CY", "Current Ratio PY", \
                         "Shares Issued CY", "Shares Issued PY", "Gross margin CY", "Gross margin PY", \
                         "Asset Turnover CY", "Asset Turnover PY"]

    df = pd.DataFrame(df_data)

    # Assign the 9 metrics a value of 1, 0 or None if the data is missing
    df.loc[0, "Positive Net Income"] = [None if x is None else 1 if x > 0 else 0 for x in df["Net Income"]]
    if df_data["Return On Assets CY"] is None or df_data["Return On Assets PY"] is None:
        df.loc[0, "Positive Return On Assets"] = None
    else:
        df.loc[0, "Positive Return On Assets"] = np.where(df["Return On Assets CY"] > df["Return On Assets PY"], 1, 0)
    if df_data["Oper Cash Flow"] is None:
        df.loc[0, "Positive Oper Cash Flow"] = None
    else:
        df.loc[0, "Positive Oper Cash Flow"] = np.where(df["Oper Cash Flow"] > 0, 1, 0)
    if df_data["Oper Cash Flow vs Net Income"] is None:
        df.loc[0, "Oper Cash Flow higher than Net Income"] = None
    else:
        df.loc[0, "Oper Cash Flow higher than Net Income"] = np.where(df["Oper Cash Flow vs Net Income"] > 0, 1, 0)
    df.loc[0, "Decrease in Leverage"] = [None if x is None else 1 if x < 0 else 0 for x in df["Leverage CY - PY"]]
    if df_data["Current Ratio CY"] is None or df_data["Current Ratio PY"] is None:
        df.loc[0, "Increase in Current Ratio"] = None
    else:
        df.loc[0, "Increase in Current Ratio"] = np.where(df["Current Ratio CY"] > df["Current Ratio PY"], 1, 0)
    if df_data["Shares Issued CY"] is None or df_data["Shares Issued PY"] is None:
        df.loc[0, "No Shares Issued"] = None
    else:
        df.loc[0, "No Shares Issued"] = np.where(df["Shares Issued CY"] <= df["Shares Issued PY"], 1, 0)
    if df_data["Gross margin CY"] is None or df_data["Gross margin PY"] is None:
        df.loc[0, "Increase in Gross Margin"] = None
    else:
        df.loc[0, "Increase in Gross Margin"] = np.where(df["Gross margin CY"] > df["Gross margin PY"], 1, 0)
    if df_data["Asset Turnover CY"] is None or df_data["Asset Turnover PY"] is None:
        df.loc[0, "Increase in Asset Turnover"] = None
    else:
        df.loc[0, "Increase in Asset Turnover"] = np.where(df["Asset Turnover CY"] > df["Asset Turnover PY"], 1, 0)

    # Step 4
    scores = {
        1: df.loc[0, "Positive Net Income"],
        2: df.loc[0, "Positive Return On Assets"],
        3: df.loc[0, "Positive Oper Cash Flow"],
        4: df.loc[0, "Oper Cash Flow higher than Net Income"],
        5: df.loc[0, "Decrease in Leverage"],
        6: df.loc[0, "Increase in Current Ratio"],
        7: df.loc[0, "No Shares Issued"],
        8: df.loc[0, "Increase in Gross Margin"],
        9: df.loc[0, "Increase in Asset Turnover"],
    }

    # drop the columns we don't need anymore
    df.drop(columns=columns_to_delete, inplace=True)

    # This variables contains the number of metrics out of 9 having a value of 1 or 0; None is discarded
    valid_scores = 0
    for value in scores.items():
        if value[1] == 1 or value[1] == 0:
            valid_scores += 1

    # This variable contains the number of positive metrics
    pos_scores = 0
    for value in scores.items():
        if value[1] == 1:
            pos_scores += 1

    # Step 5
    piotroski_score = str(pos_scores) + "/" + str(valid_scores)
    pos_net_income = df._get_value(0, "Positive Net Income")
    pos_roa = df._get_value(0, "Positive Return On Assets")
    pos_oper_cashflow = df._get_value(0, "Positive Oper Cash Flow")
    oper_cashflow_vs_net_income = df._get_value(0, "Oper Cash Flow higher than Net Income")
    decrease_leverage = df._get_value(0, "Decrease in Leverage")
    increase_current_ratio = df._get_value(0, "Increase in Current Ratio")
    no_shares_issued = df._get_value(0, "No Shares Issued")
    increase_gross_margin = df._get_value(0, "Increase in Gross Margin")
    increase_asset_turnover = df._get_value(0, "Increase in Asset Turnover")

    if int(pos_scores) >= 8:
        print("\n" + ticker_to_use + " based on year: " + str(last_year))
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
    else:
        print(ticker_to_use + ": " + str(piotroski_score) + "\n")


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


if __name__ == '__main__':
    print_hi('PyCharm')
