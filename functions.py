import pandas as pd
import yfinance as yf
import numpy as np


def get_fundamentals(ticker: str) -> list:
    """
    This function first tries to download the data from yfinance, if successful
    it will split the data into 3 variables, one for each statement.
    For each variable, the last available year will be compared with "2023" or "2024"
    and it will be checked whether it contains 4 years. If so
    the column will be renamed to "2023", "2022"... or "2024", "2023"...
    :param: ticker
    :return: if the last year available == "2023" or "2024" AND it contains 4 years it returns a list [True, inc_stat...]
             else it returns [False, [], [], [], ""]
    """
    try:
        stock_data = yf.Ticker(ticker)
    except Exception as e:
        return [False, [], [], [], ""]
    inc_stat = stock_data.income_stmt
    balance_sheet = stock_data.balance_sheet
    cash_flow = stock_data.cashflow

    # the last year available for all statements
    last_year_inc_stat = str(pd.to_datetime(inc_stat.columns[0]).year)
    last_year_bal_sheet = str(pd.to_datetime(balance_sheet.columns[0]).year)
    last_year_cash_flow = str(pd.to_datetime(cash_flow.columns[0]).year)

    # check for the 3 statements whether there are all 4 years and the last year is 2023 or 2024
    # 4 years and last year == 2023
    if len(inc_stat.columns) == 4 and len(balance_sheet.columns) == 4 and len(cash_flow.columns) == 4:
        if last_year_inc_stat == "2023" and last_year_bal_sheet == "2023" and last_year_cash_flow == "2023":
            inc_stat.columns = ["2023", "2022", "2021", "2020"]
            balance_sheet.columns = ["2023", "2022", "2021", "2020"]
            cash_flow.columns = ["2023", "2022", "2021", "2020"]
            return [True, inc_stat, balance_sheet, cash_flow, "2023"]
    # 4 years and last year == 2024
    elif len(inc_stat.columns) == 4 and len(balance_sheet.columns) == 4 and len(cash_flow.columns) == 4:
        if last_year_inc_stat == "2024" and last_year_bal_sheet == "2024" and last_year_cash_flow == "2024":
            inc_stat.columns = ["2024", "2023", "2022", "2021"]
            balance_sheet.columns = ["2024", "2023", "2022", "2021"]
            cash_flow.columns = ["2024", "2023", "2022", "2021"]
            return [True, inc_stat, balance_sheet, cash_flow, "2024"]
        else:
            return [False, [], [], [], ""]
    # more than 4 years and last year == 2023 or last year == 2024
    elif len(inc_stat.columns) > 4 or len(balance_sheet.columns) > 4 or len(cash_flow.columns) > 4:
        if last_year_inc_stat == "2023" and last_year_bal_sheet == "2023" and last_year_cash_flow == "2023":
            inc_stat = inc_stat.iloc[:, [0, 1, 2, 3]]
            inc_stat.columns = ["2023", "2022", "2021", "2020"]
            balance_sheet = balance_sheet.iloc[:, [0, 1, 2, 3]]
            balance_sheet.columns = ["2023", "2022", "2021", "2020"]
            cash_flow = cash_flow.iloc[:, [0, 1, 2, 3]]
            cash_flow.columns = ["2023", "2022", "2021", "2020"]
            return [True, inc_stat, balance_sheet, cash_flow, "2023"]
        elif last_year_inc_stat == "2024" and last_year_bal_sheet == "2024" and last_year_cash_flow == "2024":
            inc_stat = inc_stat.iloc[:, [0, 1, 2, 3]]
            inc_stat.columns = ["2024", "2023", "2022", "2021"]
            balance_sheet = balance_sheet.iloc[:, [0, 1, 2, 3]]
            balance_sheet.columns = ["2024", "2023", "2022", "2021"]
            cash_flow = cash_flow.iloc[:, [0, 1, 2, 3]]
            cash_flow.columns = ["2024", "2023", "2022", "2021"]
            return [True, inc_stat, balance_sheet, cash_flow, "2024"]
        else:
            return [False, [], [], [], ""]
    else:
        return [False, [], [], [], ""]
