import pandas as pd
from datetime import datetime, timedelta

def calcExcess(df):
    # df must have portfolio values
    df['Portfolio Growth'] = df['Portfolio Value'].pct_change()
    df['SP5 Portfolio Growth'] = df['SP5 Portfolio Value'].pct_change()
    df['R3V Portfolio Growth'] = df['R3V Portfolio Value'].pct_change()
    df['SP5E Portfolio Growth'] = df['SP5E Portfolio Value'].pct_change()

    # excess performance
    df['Portfolio Excess vs SP5'] = df['Portfolio Growth'] - df['SP5 Portfolio Growth']
    df['Portfolio Excess vs R3V'] = df['Portfolio Growth'] - df['R3V Portfolio Growth']
    df['Portfolio Excess vs SP5E'] = df['Portfolio Growth'] - df['SP5E Portfolio Growth']

def transformDaily(df_daily, df_benchmarks):
    # join with S&P price dataframe
    temp = pd.merge(df_daily, df_benchmarks, on='Date', how='left')

    # set all portfolio values equal when cash first runs out
    full = (temp['Cash'] == 0).idxmax()
    temp['SP5 Portfolio Value'] = temp.at[full, 'Portfolio Value']
    temp['R3V Portfolio Value'] = temp.at[full, 'Portfolio Value']
    temp['SP5E Portfolio Value'] = temp.at[full, 'Portfolio Value']

    # create column for S&P 500 & Russell 3000 portfolio value
    sp5_growth_factor = temp['SP5'] / temp.at[full, 'SP5']
    r3v_growth_factor = temp['R3V'] / temp.at[full, 'R3V']
    sp5e_growth_factor = temp['SP5E'] / temp.at[full, 'SP5E']

    temp['SP5 Portfolio Value'] = temp['SP5 Portfolio Value'] * sp5_growth_factor
    temp['R3V Portfolio Value'] = temp['R3V Portfolio Value'] * r3v_growth_factor
    temp['SP5E Portfolio Value'] = temp['SP5E Portfolio Value'] * sp5e_growth_factor

    calcExcess(temp)

    return temp

def getMonthly(df_daily):
    # create then group by year-month
    #df_daily['YearMonth'] = df_daily['Date'].dt.strftime('%Y-%m')
    temp = df_daily.groupby(df_daily['Date'].dt.strftime('%Y-%m')).agg({'Cash': 'last',
                                                                        'Portfolio Value': 'last',
                                                                        'Positions Count': 'last',
                                                                        'Position Max Age (M)': 'last',
                                                                        'Position Average Age (M)': 'last',
                                                                        'New Position Count': 'sum', 
                                                                        'SP5': 'last',
                                                                        'R3V': 'last',
                                                                        'SP5E': 'last',
                                                                        'SP5 Portfolio Value': 'last',
                                                                        'R3V Portfolio Value': 'last',
                                                                        'SP5E Portfolio Value': 'last'}).reset_index()
    
    # add excess returns
    calcExcess(temp)

    return temp

def calcPerfHelper(df_daily, start_str, end_str):
    # convert to dates
    start_date = datetime.strptime(start_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_str, "%Y-%m-%d")

    # number of years between dates
    years = ((end_date - start_date).days) / 365.25

    # filter dataframe
    temp = df_daily[(df_daily['Date'] == start_date) | (df_daily['Date'] == end_date)]

    # start and end values
    portfolio_start = temp['Portfolio Value'].iloc[0]
    portfolio_end = temp['Portfolio Value'].iloc[1]

    sp5_start = temp['SP5 Portfolio Value'].iloc[0]
    sp5_end = temp['SP5 Portfolio Value'].iloc[1]

    r3v_start = temp['R3V Portfolio Value'].iloc[0]
    r3v_end = temp['R3V Portfolio Value'].iloc[1]

    sp5e_start = temp['SP5E Portfolio Value'].iloc[0]
    sp5e_end = temp['SP5E Portfolio Value'].iloc[1]


    # regular & annualised returns
    portfolio_returns = (portfolio_end/portfolio_start) - 1
    sp5_returns = (sp5_end/sp5_start) - 1
    r3v_returns = (r3v_end/r3v_start) - 1
    
    portfolio_returns_ann = (1+portfolio_returns)**(1/years) - 1
    sp5_returns_ann = (1+sp5_returns)**(1/years) - 1
    r3v_returns_ann = (1+r3v_returns)**(1/years) - 1

    # regular & annualised excess returns
    sp5_ex_returns = portfolio_returns - sp5_returns
    r3v_ex_returns = portfolio_returns - r3v_returns
    
    sp5_ex_returns_ann = portfolio_returns_ann - sp5_returns_ann
    r3v_ex_returns_ann = portfolio_returns_ann - r3v_returns_ann
    
    # outperformer
    sp5_outperformer = (sp5_ex_returns_ann > 0)*1
    rs3_outperformer = (r3v_ex_returns_ann > 0)*1
    
    # if sp5e is 0, set everything to na (TO BE IMPROVED)
    if sp5e_end == 0 or sp5e_start == 0:
        sp5e_returns = sp5e_returns_ann = sp5e_ex_returns = sp5e_ex_returns_ann = sp5e_outperformer = 'na'
    else:
        sp5e_returns = (sp5e_end/sp5e_start) - 1
        sp5e_returns_ann = (1+sp5e_returns)**(1/years) - 1
        sp5e_ex_returns = portfolio_returns - sp5e_returns
        sp5e_ex_returns_ann = portfolio_returns_ann - sp5e_returns_ann
        sp5e_outperformer = (sp5e_ex_returns_ann > 0)*1

    return [start_date, end_date, years, 
            portfolio_start, portfolio_end, portfolio_returns, portfolio_returns_ann, 
            sp5_start, sp5_end, sp5_returns, sp5_returns_ann, sp5_ex_returns, sp5_ex_returns_ann, sp5_outperformer,
            r3v_start, r3v_end, r3v_returns, r3v_returns_ann, r3v_ex_returns, r3v_ex_returns_ann, rs3_outperformer,
            sp5e_start, sp5e_end, sp5e_returns, sp5e_returns_ann, sp5e_ex_returns, sp5e_ex_returns_ann, sp5e_outperformer]

def calcPerf(df_daily, date_pairs):

    returns_list = []
    returns_columns = ['Start Date', 'End Date', 'Years', 
                       'Portfolio Start Val', 'Portfolio End Val', 'Portfolio Returns', 'Portfolio Returns Ann',
                       'SP5 Portfolio Start Val', 'SP5 Portfolio End Val', 'SP5 Portfolio Returns', 'SP5 Portfolio Returns Ann', 'Portfolio Excess vs SP5', 'Portfolio Excess vs SP5 Ann', 'Outperformed SP5',
                       'R3V Portfolio Start Val', 'R3V Portfolio End Val', 'R3V Portfolio Returns', 'R3V Portfolio Returns Ann', 'Portfolio Excess vs R3V', 'Portfolio Excess vs R3V Ann', 'Outperformed R3V',
                       'SP5E Portfolio Start Val', 'SP5E Portfolio End Val', 'SP5E Portfolio Returns', 'SP5E Portfolio Returns Ann', 'Portfolio Excess vs SP5E', 'Portfolio Excess vs SP5E Ann', 'Outperformed SP5E']

    # loop through date intervals to get performance
    for pair in date_pairs:
        start_date, end_date = pair
        temp = calcPerfHelper(df_daily, start_date, end_date)
        returns_list.append(temp)

    # create dataframe
    returns_df = pd.DataFrame(returns_list, columns=returns_columns)

    return returns_df

def createReturnsDf(df_daily):
    date_pairs = [['2011-01-01', '2023-10-01'], ['2008-01-01', '2009-03-01'], ['2018-01-01', '2019-01-01'], 
                  ['2020-01-01', '2020-04-01'], ['2020-04-01', '2021-01-01'], ['2022-01-01', '2023-01-01'],

                  ['2010-12-31', '2011-12-31'], ['2011-12-31', '2012-12-31'], ['2012-12-31', '2013-12-31'], ['2013-12-31', '2014-12-31'],
                  ['2014-12-31', '2015-12-31'], ['2015-12-31', '2016-12-31'], ['2016-12-31', '2017-12-31'], ['2017-12-31', '2018-12-31'],
                  ['2018-12-31', '2019-12-31'], ['2019-12-31', '2020-12-31'], ['2020-12-31', '2021-12-31'], ['2021-12-31', '2022-12-31'],
                  ['2022-12-31', '2023-10-01'],

                  ['2010-12-31', '2013-12-31'], ['2011-12-31', '2014-12-31'], ['2012-12-31', '2015-12-31'], ['2013-12-31', '2016-12-31'],
                  ['2014-12-31', '2017-12-31'], ['2015-12-31', '2018-12-31'], ['2016-12-31', '2019-12-31'], ['2017-12-31', '2020-12-31'],
                  ['2018-12-31', '2021-12-31'], ['2019-12-31', '2022-12-31']]
    
    temp = calcPerf(df_daily, date_pairs)

    # add hardcoded names
    era_names = ['2011+', 'GFC', '2018', 'Into COVID', 'Out of COVID', '2022',
                 
                 '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018',
                 '2019', '2020', '2021', '2022', '2023 YTD',

                 '2011+3', '2012+3', '2013+3', '2014+3', '2015+3', '2016+3', '2017+3', '2018+3', '2019+3', '2020+3']
    
    temp.insert(0, 'Eras', era_names)

    return temp

def transformSold(df_daily, df_sold):
    # calculate performance
    df_sold['Holding Period (Years)'] = (df_sold['Sell Date'] - df_sold['Buy Date']) / 365.25
    df_sold['Performance'] = (df_sold['Sell Price'] / df_sold['Buy Price']) - 1

    # convert date column types
    df_sold['Sell Date'] = df_sold['Sell Date'].dt.strftime('%Y-%m-%d')
    df_sold['Buy Date'] = df_sold['Buy Date'].dt.strftime('%Y-%m-%d')

    # add benchmark performances
    date_pairs = list(zip(df_sold['Buy Date'],df_sold['Sell Date']))
    temp = calcPerf(df_daily, date_pairs)

    temp['Start Date'] = temp['Start Date'].dt.strftime('%Y-%m-%d')
    temp['End Date'] = temp['End Date'].dt.strftime('%Y-%m-%d')
    
    output = df_sold.merge(temp, how='left', left_on=['Buy Date', 'Sell Date'], right_on=['Start Date','End Date'])
    
    return output