import pandas as pd
import yfinance as yf
import numpy as np
import sys


def dict_from_two_lists(lst1: list, lst2: list):
    """
    From two lists it will create a dictionary with keys/values
    :param lst1: a list of keys
    :param lst2: a list of values
    :return: a dictionary
    """
    dictionary = dict(zip(lst1, lst2))

    return dictionary


def find_industry_pe_ratio():
    """
    This function will scan the webpage https://fullratio.com/pe-ratio-by-industry to
    download the average PE ratio per industry and will create a dictionary
    industry/pe_ratio.
    The assumption is that there are 122 industries, but the number must be checked manually
    :return: the dictionary with industry (key) / pe_ratio (value)
    """
    webpage = pd.read_html('https://fullratio.com/pe-ratio-by-industry')

    # there are 122 industries: extract the 2 columns we are interested in
    industry_column = str(webpage[0]["Industry"])
    pe_column = str(webpage[0]["Average P/E ratio"])

    # split the industry string into 122 substring and strip the leading and trailing white spaces
    industries = []
    start = 3
    end = 48
    for s in range(0, 122):
        industry = industry_column[start:end].strip()
        industries.append(industry)
        start += 48
        end += 48

    # split the pe_ratio string into 122 substring and strip the leading and trailing white spaces
    pe_ratios = []
    pe_start = 3
    pe_end = 13
    for s in range(0, 122):
        pe = pe_column[pe_start:pe_end].strip()
        pe_ratios.append(pe)
        pe_start += 13
        pe_end += 13

    return industries, pe_ratios


def write_list_to_txt(lst: list, title: str):
    with open(f'{title}.txt', 'w+') as f:
        for items in lst:
            f.write('%s\n' %items)
    f.close()


def get_ticker_info(ticker: str):
    """
    This function will download the ticker data and will extract the needed values:
    industry, sector, country, price, book value, price/book ratio, PE ratio, PEG ratio.
    :param ticker: ticker name as a string
    :return: a list of 8 items
    """
    # download the ticker data
    data = yf.Ticker(ticker)

    if data:
        try:
            industry = data.info["industry"]
        except:
            industry = None
        try:
            sector = data.info["sector"]
        except:
            sector = None
        try:
            country = data.info["country"]
        except:
            country = None

        try:
            price = round(data.info["currentPrice"], 2)
        except:
            price = None

        try:
            bookValue = round(data.info["bookValue"], 2)
        except:
            bookValue = None

        if price and bookValue:
            pb_ratio = round(price / bookValue, 3)
        else:
            pb_ratio = None

        try:
            trailingpe = float(round(data.info["trailingPE"], 2))
        except:
            trailingpe = None

        try:
            peg = round(data.info["pegRatio"], 2)
        except:
            peg = None
    else:
        return [None, None, None, None, None, None, None, None]

    return [industry, sector, country, price, bookValue, pb_ratio, trailingpe, peg]


def get_fundamentals(ticker: str) -> list:
    """
    This function first tries to download the data from yfinance, if successful
    it will split the data into 3 variables, one for each statement.
    For each variable, the last available year will be compared with "2023" or "2024"
    and it will be checked how many years of data it shows.

    There are different possible combinations:
    - ideally the three statements contain 4 years;
    - sometimes there are > 4 years, if so only the last 4 will be used;
    - elif at least one statement has 3 years, only 3 years will be used;
    - elif at least one statement has 2 years, only 2 years will be used;
    - else there are less than 2 years of data, the ticker will return a list with no data.

    :param: a ticker
    :return: a list like [True, inc_stat, balance_sheet, cash_flow, "2023", 4]
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

    # at least one statement has more than 4 years (the others no less than 4) and last year == 2023 or last year == 2024
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

    # at least one statement has 3 years and the others at least 3 or more
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

    # at least one statement has 2 years and the others at least 2 or more
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
