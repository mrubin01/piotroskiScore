import pandas as pd
import yfinance as yf
import numpy as np
import sys


def get_fundamentals(ticker: str) -> list:
    """
    This function first tries to download the data from yfinance, if successful
    it will split the data into 3 variables, one for each statement.
    For each variable, the last available year will be compared with "2023" or "2024"
    and it will be checked how many years it shows.
    Ideally the three statements should contain 4 years, anyway if more only the last 4 will be used, if
    less only those available, but at least 2 years.
    :param: ticker
    :return: a list [True, inc_stat, balance_sheet, cash_flow, "2024", 4]
             else it returns [False, [], [], [], "", None]
    """
    try:
        stock_data = yf.Ticker(ticker)
    except Exception as e:
        return [False, [], [], [], "", None]
    inc_stat = stock_data.income_stmt
    balance_sheet = stock_data.balance_sheet
    cash_flow = stock_data.cashflow

    # the last year available for all statements
    try:
        last_year_inc_stat = str(pd.to_datetime(inc_stat.columns[0]).year)
        last_year_bal_sheet = str(pd.to_datetime(balance_sheet.columns[0]).year)
        last_year_cash_flow = str(pd.to_datetime(cash_flow.columns[0]).year)
    except Exception as e:
        return [False, [], [], [], "", None]

    # how many years available
    try:
        inc_stat_len = len(inc_stat.columns)
        bal_sheet_len = len(balance_sheet.columns)
        cash_flow_len = len(cash_flow.columns)
    except Exception as e:
        return [False, [], [], [], "", None]

    # check for the 3 statements whether they have all 4 years and the last year is 2023 or 2024
    # 4 years and last year == 2023 or last year == 2024: rename the columns with only Year
    if inc_stat_len == 4 and bal_sheet_len == 4 and cash_flow_len == 4:
        if last_year_inc_stat == "2023" and last_year_bal_sheet == "2023" and last_year_cash_flow == "2023":
            inc_stat.columns = ["2023", "2022", "2021", "2020"]
            balance_sheet.columns = ["2023", "2022", "2021", "2020"]
            cash_flow.columns = ["2023", "2022", "2021", "2020"]
            return [True, inc_stat, balance_sheet, cash_flow, "2023", 4]
        elif last_year_inc_stat == "2024" and last_year_bal_sheet == "2024" and last_year_cash_flow == "2024":
            inc_stat.columns = ["2024", "2023", "2022", "2021"]
            balance_sheet.columns = ["2024", "2023", "2022", "2021"]
            cash_flow.columns = ["2024", "2023", "2022", "2021"]
            return [True, inc_stat, balance_sheet, cash_flow, "2024", 4]
        else:
            return [False, [], [], [], "", None]
    # any statement has more than 4 years (the other no less than 4) and last year == 2023 or last year == 2024
    # only the last 4 years will be used and the columns renamed with only Year
    elif (inc_stat_len > 4 or bal_sheet_len > 4 or cash_flow_len > 4) and \
            (inc_stat_len >= 4 and bal_sheet_len >= 4 and cash_flow_len >= 4):
        if last_year_inc_stat == "2023" and last_year_bal_sheet == "2023" and last_year_cash_flow == "2023":
            inc_stat = inc_stat.iloc[:, [0, 1, 2, 3]]
            inc_stat.columns = ["2023", "2022", "2021", "2020"]
            balance_sheet = balance_sheet.iloc[:, [0, 1, 2, 3]]
            balance_sheet.columns = ["2023", "2022", "2021", "2020"]
            cash_flow = cash_flow.iloc[:, [0, 1, 2, 3]]
            cash_flow.columns = ["2023", "2022", "2021", "2020"]
            return [True, inc_stat, balance_sheet, cash_flow, "2023", 4]
        elif last_year_inc_stat == "2024" and last_year_bal_sheet == "2024" and last_year_cash_flow == "2024":
            inc_stat = inc_stat.iloc[:, [0, 1, 2, 3]]
            inc_stat.columns = ["2024", "2023", "2022", "2021"]
            balance_sheet = balance_sheet.iloc[:, [0, 1, 2, 3]]
            balance_sheet.columns = ["2024", "2023", "2022", "2021"]
            cash_flow = cash_flow.iloc[:, [0, 1, 2, 3]]
            cash_flow.columns = ["2024", "2023", "2022", "2021"]
            return [True, inc_stat, balance_sheet, cash_flow, "2024", 4]
        else:
            return [False, [], [], [], "", None]
    # any statement has 3 years and the others at least 3 or more
    # only the last 3 years will be used and the columns renamed with only Year
    elif (inc_stat_len == 3 or bal_sheet_len == 3 or cash_flow_len == 3) and \
            (inc_stat_len >= 3 and bal_sheet_len >= 3 and cash_flow_len >= 3):
        if last_year_inc_stat == "2023" and last_year_bal_sheet == "2023" and last_year_cash_flow == "2023":
            inc_stat = inc_stat.iloc[:, [0, 1, 2]]
            inc_stat.columns = ["2023", "2022", "2021"]
            balance_sheet = balance_sheet.iloc[:, [0, 1, 2]]
            balance_sheet.columns = ["2023", "2022", "2021"]
            cash_flow = cash_flow.iloc[:, [0, 1, 2]]
            cash_flow.columns = ["2023", "2022", "2021"]
            return [True, inc_stat, balance_sheet, cash_flow, "2023", 3]
        elif last_year_inc_stat == "2024" and last_year_bal_sheet == "2024" and last_year_cash_flow == "2024":
            inc_stat = inc_stat.iloc[:, [0, 1, 2]]
            inc_stat.columns = ["2024", "2023", "2020"]
            balance_sheet = balance_sheet.iloc[:, [0, 1, 2]]
            balance_sheet.columns = ["2024", "2023", "2020"]
            cash_flow = cash_flow.iloc[:, [0, 1, 2]]
            cash_flow.columns = ["2024", "2023", "2020"]
            return [True, inc_stat, balance_sheet, cash_flow, "2024", 3]
        else:
            return [False, [], [], [], "", None]
    # any statement has 2 years and the others at least 2 or more
    # only the last 2 years will be used and the columns renamed with only Year
    elif (inc_stat_len == 2 or bal_sheet_len == 2 or cash_flow_len == 2) \
        and (inc_stat_len >= 2 and bal_sheet_len >= 2 and cash_flow_len >= 2):
        if last_year_inc_stat == "2023" and last_year_bal_sheet == "2023" and last_year_cash_flow == "2023":
            inc_stat = inc_stat.iloc[:, [0, 1]]
            inc_stat.columns = ["2023", "2022"]
            balance_sheet = balance_sheet.iloc[:, [0, 1]]
            balance_sheet.columns = ["2023", "2022"]
            cash_flow = cash_flow.iloc[:, [0, 1]]
            cash_flow.columns = ["2023", "2022"]
            return [True, inc_stat, balance_sheet, cash_flow, "2023", 2]
        elif last_year_inc_stat == "2024" and last_year_bal_sheet == "2024" and last_year_cash_flow == "2024":
            inc_stat = inc_stat.iloc[:, [0, 1]]
            inc_stat.columns = ["2024", "2023"]
            balance_sheet = balance_sheet.iloc[:, [0, 1]]
            balance_sheet.columns = ["2024", "2023"]
            cash_flow = cash_flow.iloc[:, [0, 1]]
            cash_flow.columns = ["2024", "2023"]
            return [True, inc_stat, balance_sheet, cash_flow, "2024", 2]
        else:
            return [False, [], [], [], "", None]
    else:
        return [False, [], [], [], "", None]
