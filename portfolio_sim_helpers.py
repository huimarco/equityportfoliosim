import pandas as pd
from datetime import datetime, timedelta

def transformDaily(df_daily, df_benchmarks):
    # join with S&P price dataframe
    temp = pd.merge(df_daily, df_benchmarks, on='Date', how='left')

    # set both portfolio values equal when cash first runs out
    full = (temp['Cash'] == 0).idxmax()
    sp_growth_factor = temp['S&P 500 Price'] / temp.at[full, 'S&P 500 Price']
    rus_growth_factor = temp['Russell 3000 Price'] / temp.at[full, 'Russell 3000 Price']
    temp['S&P Portfolio Value'] = temp.at[full, 'Portfolio Value']
    temp['Russell Portfolio Value'] = temp.at[full, 'Portfolio Value']

    # create column for S&P 500 & Russell 3000 portfolio value
    temp['S&P Portfolio Value'] = temp['S&P Portfolio Value'] * sp_growth_factor
    temp['Russell Portfolio Value'] = temp['Russell Portfolio Value'] * rus_growth_factor

    return temp

def getMonthly(df_daily):
    # create then group by year-month
    #df_daily['YearMonth'] = df_daily['Date'].dt.strftime('%Y-%m')
    output = df_daily.groupby(df_daily['Date'].dt.strftime('%Y-%m')).agg({'Cash': 'last',
                                                                          'Portfolio Value': 'last',
                                                                          'Positions Count': 'last',
                                                                          'Position Max Age': 'last',
                                                                          'Position Average Age': 'last',
                                                                          'New Position Count': 'sum', 
                                                                          'S&P Portfolio Value': 'last',
                                                                          'Russell Portfolio Value': 'last',}).reset_index()
    
    # change in portfolio values
    output['Portfolio Growth'] = output['Portfolio Value'].pct_change()
    output['S&P Portfolio Growth'] = output['S&P Portfolio Value'].pct_change()
    output['Russell Portfolio Growth'] = output['Russell Portfolio Value'].pct_change()

    # excess performance
    output['S&P Excess Growth'] = output['Portfolio Growth'] - output['S&P Portfolio Growth']
    output['Russell Excess Growth'] = output['Portfolio Growth'] - output['S&P Portfolio Growth']

    return output

def transformSold(df_sold):
    df_sold['Holding Period (Years)'] = (df_sold['Sell Date'] - df_sold['Buy Date']) / 365.25
    df_sold['Performance'] = (df_sold['Sell Price'] / df_sold['Buy Price']) - 1
    return df_sold

def calcPerfHelper(df_daily, start_str, end_str):
    # convert to dates
    start_date = datetime.strptime(start_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_str, "%Y-%m-%d")

    # number of years between dates
    years = ((end_date - start_date).days) / 365.25

    # filter dataframe
    temp = df_daily[(df_daily['Date'] == start_date) | (df_daily['Date'] == end_date)]

    # portfolio start and end values
    portfolio_start = temp['Portfolio Value'].iloc[0]
    portfolio_end = temp['Portfolio Value'].iloc[1]

    # S&P 500 portfolio start and end values
    sp_start = temp['S&P Portfolio Value'].iloc[0]
    sp_end = temp['S&P Portfolio Value'].iloc[1]

    # Russell 3000 portfolio start and end values
    rus_start = temp['Russell Portfolio Value'].iloc[0]
    rus_end = temp['Russell Portfolio Value'].iloc[1]

    # returns & excess returns
    portfolio_returns = (portfolio_end/portfolio_start) - 1
    sp_returns = (sp_end/sp_start) - 1
    rus_returns = (rus_start/rus_end) - 1
    sp_excess_returns = portfolio_returns - sp_returns
    rus_excess_returns = portfolio_returns - rus_returns

    # annualised returns
    portfolio_returns_ann = (1+portfolio_returns)**(1/years) - 1
    sp_returns_ann = (1+sp_returns)**(1/years) - 1
    rus_returns_ann = (1+rus_returns)**(1/years) - 1

    sp_excess_returns_ann = portfolio_returns_ann - sp_returns_ann
    rus_excess_returns_ann = portfolio_returns_ann - rus_returns_ann

    sp_outperformer = (sp_excess_returns_ann > 0)*1
    rus_outperformer = (rus_excess_returns_ann > 0)*1

    return [start_date, end_date, years, 
            portfolio_start, portfolio_end, portfolio_returns, portfolio_returns_ann, 
            sp_start, sp_end, sp_returns, sp_returns_ann,
            sp_excess_returns, sp_excess_returns_ann, sp_outperformer,
            rus_start, rus_end, rus_returns, rus_returns_ann,
            rus_excess_returns, rus_excess_returns_ann, rus_outperformer]

def calcPerf(df_daily):
    date_pairs = [['2011-01-01', '2023-10-01'], ['2008-01-01', '2009-03-01'], ['2018-01-01', '2019-01-01'], 
                  ['2020-01-01', '2020-04-01'], ['2020-04-01', '2021-01-01'], ['2022-01-01', '2023-01-01'],

                  ['2010-12-31', '2011-12-31'], ['2011-12-31', '2012-12-31'], ['2012-12-31', '2013-12-31'], ['2013-12-31', '2014-12-31'],
                  ['2014-12-31', '2015-12-31'], ['2015-12-31', '2016-12-31'], ['2016-12-31', '2017-12-31'], ['2017-12-31', '2018-12-31'],
                  ['2018-12-31', '2019-12-31'], ['2019-12-31', '2020-12-31'], ['2020-12-31', '2021-12-31'], ['2021-12-31', '2022-12-31'],
                  ['2022-12-31', '2023-10-01'],

                  ['2010-12-31', '2013-12-31'], ['2011-12-31', '2014-12-31'], ['2012-12-31', '2015-12-31'], ['2013-12-31', '2016-12-31'],
                  ['2014-12-31', '2017-12-31'], ['2015-12-31', '2018-12-31'], ['2016-12-31', '2019-12-31'], ['2017-12-31', '2020-12-31'],
                  ['2018-12-31', '2021-12-31'], ['2019-12-31', '2022-12-31']]

    returns_list = []
    returns_columns = ['Start Date', 'End Date', 'Years', 
                       'Portfolio Start Val', 'Portfolio End Val', 'Portfolio Returns', 'Portfolio Returns Annualized',
                       'S&P Portfolio Start Val', 'S&P Portfolio End Val', 'S&P Portfolio Returns', 'S&P Portfolio Returns Annualized',
                       'S&P Excess Returns', 'S&P Excess Returns Annualized', 'S&P Outperformer',
                       'Russell Portfolio Start Val', 'Russell Portfolio End Val', 'Russell Portfolio Returns', 'Russell Portfolio Returns Annualized',
                       'Russell Excess Returns', 'Russell Excess Returns Annualized', 'Russell Outperformer']
    
    # loop through date intervals to get performance
    for pair in date_pairs:
        start_date, end_date = pair
        temp = calcPerfHelper(df_daily, start_date, end_date)
        returns_list.append(temp)

    # create dataframe
    returns_df = pd.DataFrame(returns_list, columns=returns_columns)

    # add hardcoded names
    era_names = ['2011+', 'GFC', '2018', 'Into COVID', 'Out of COVID', '2022',
                 
                 '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018',
                 '2019', '2020', '2021', '2022', '2023 YTD',
                 
                 '2011+3', '2012+3', '2013+3', '2014+3', '2015+3', '2016+3', '2017+3', '2018+3', '2019+3', '2020+3']
    
    returns_df.insert(0, 'Eras', era_names)

    return returns_df