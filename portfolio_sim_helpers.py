import pandas as pd
from datetime import datetime, timedelta

def calcChange(df_md):
    # USE ONLY FOR MONTHLY/DAILY DF. TERRIBLE
    df_md['Sim Portfolio Growth'] = df_md['Sim Portfolio Value'].pct_change()

    benchmarks = ['SP5E', 'R3V', 'SP5']
    for i in benchmarks:
        df_md[f'{i} Portfolio Growth'] = df_md[f'{i} Portfolio Value'].pct_change()
        df_md[f'Sim Portfolio Excess vs {i}'] = df_md['Sim Portfolio Growth'] - df_md[f'{i} Portfolio Growth']

def transformDaily(df_daily, df_benchmarks):
    # join with S&P price dataframe
    temp = pd.merge(df_daily, df_benchmarks, on='Date', how='left')

    # loop through benchmarks and create columns for value
    benchmarks = ['SP5E', 'R3V', 'SP5']
    for i in benchmarks:
        # set starting value to sim portfolio value when cash runs out
        if i == 'SP5E':
             full = (temp['SP5E'] != 0).idxmax()
        else:
             full = (temp['Cash'] == 0).idxmax()
        
        temp[f'{i} Portfolio Value'] = temp.at[full, 'Sim Portfolio Value']
        # create growth factor column
        growth_factor = temp[i] / temp.at[full, i]
        # create value column
        temp[f'{i} Portfolio Value'] = temp[f'{i} Portfolio Value'] * growth_factor

    calcChange(temp)

    return temp

def getMonthly(df_daily):
    #group by year-month
    temp = df_daily.groupby(df_daily['Date'].dt.strftime('%Y-%m')).agg({'Cash': 'last',
                                                                        'Sim Portfolio Value': 'last',
                                                                        'Positions Count': 'last',
                                                                        'Position Max Age (M)': 'last',
                                                                        'Position Average Age (M)': 'last',
                                                                        'New Position Count': 'sum', 
                                                                        'SP5E': 'last',
                                                                        'R3V': 'last',
                                                                        'SP5': 'last',
                                                                        'SP5E Portfolio Value': 'last',
                                                                        'R3V Portfolio Value': 'last',
                                                                        'SP5 Portfolio Value': 'last'}).reset_index()
    
    # add excess returns
    calcChange(temp)

    return temp

def calcReturnsHelper(df_daily, start_str, end_str):
    # NEED TO BUILD BETTER CHECKS FOR METRICS

    # convert to dates
    start_date = datetime.strptime(start_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_str, "%Y-%m-%d")

    # number of years between dates
    years = ((end_date - start_date).days) / 365.25

    # filter dataframe
    temp = df_daily[(df_daily['Date'] == start_date) | (df_daily['Date'] == end_date)]

    # initialize returns lists
    returns_list = [start_date, end_date, years]

    metrics = ['Sim Portfolio Value', 'SP5E', 'R3V', 'SP5']
    for i in metrics:
        # extract start and end values
        start_val = temp[i].iloc[0]
        end_val = temp[i].iloc[1]

        # calculate gross and annualized returns
        if start_val == 0:
            returns = 999
            returns_ann = 999
        else:
            returns = (end_val/start_val) - 1
            returns_ann = (1+returns)**(1/years) - 1
        
        returns_list.extend([None, start_val, end_val, returns, returns_ann])

    return returns_list

def calcReturns(df_daily, date_pairs):
    returns_list = []
    returns_columns = ['Start Date', 'End Date', 'Years', 
                       'Empty1', 'Sim Start Val', 'Sim End Val', 'Sim Returns', 'Sim Returns Ann',
                       'Empty2', 'SP5E Start Val', 'SP5E End Val', 'SP5E Returns', 'SP5E Returns Ann',
                       'Empty3', 'R3V Start Val', 'R3V End Val', 'R3V Returns', 'R3V Returns Ann',
                       'Empty4', 'SP5 Start Val', 'SP5 End Val', 'SP5 Returns', 'SP5 Returns Ann']

    # loop through date intervals to get performance
    for pair in date_pairs:
        start_date, end_date = pair
        temp = calcReturnsHelper(df_daily, start_date, end_date)
        returns_list.append(temp)

    # create dataframe
    returns_df = pd.DataFrame(returns_list, columns=returns_columns)

    return returns_df

def calcExcess(df_returns):
    # USE ONLY FOR RETURNS DF. TERRIBLE
    df_returns['Empty5'] = None
    df_returns['Excess of SP5E'] = df_returns['Sim Returns'] - df_returns['SP5E Returns']
    df_returns['Excess of R3V'] = df_returns['Sim Returns'] - df_returns['R3V Returns']
    df_returns['Excess of SP5'] = df_returns['Sim Returns'] - df_returns['SP5 Returns']
    
    df_returns['Empty6'] = None
    df_returns['Excess of SP5E Ann'] = df_returns['Sim Returns Ann'] - df_returns['SP5E Returns Ann']
    df_returns['Excess of R3V Ann'] = df_returns['Sim Returns Ann'] - df_returns['R3V Returns Ann']
    df_returns['Excess of SP5 Ann'] = df_returns['Sim Returns Ann'] - df_returns['SP5 Returns Ann']


def createReturnsDf(df_daily):

    # find point when cash first runs out
    full = (df_daily['Cash'] == 0).idxmax()
    full_date = df_daily.at[full, 'Date']
    print(full_date)

    date_pairs = [['2008-10-04', '2023-10-01'], # NEEDS TO BE REDONE TO AVOID HARD CODING
                  ['2011-01-01', '2023-10-01'], ['2008-01-01', '2009-03-01'], ['2018-01-01', '2019-01-01'], 
                  ['2020-01-01', '2020-04-01'], ['2020-04-01', '2021-01-01'], ['2022-01-01', '2023-01-01'],

                  ['2010-12-31', '2011-12-31'], ['2011-12-31', '2012-12-31'], ['2012-12-31', '2013-12-31'], ['2013-12-31', '2014-12-31'],
                  ['2014-12-31', '2015-12-31'], ['2015-12-31', '2016-12-31'], ['2016-12-31', '2017-12-31'], ['2017-12-31', '2018-12-31'],
                  ['2018-12-31', '2019-12-31'], ['2019-12-31', '2020-12-31'], ['2020-12-31', '2021-12-31'], ['2021-12-31', '2022-12-31'],
                  ['2022-12-31', '2023-10-01'],

                  ['2010-12-31', '2013-12-31'], ['2011-12-31', '2014-12-31'], ['2012-12-31', '2015-12-31'], ['2013-12-31', '2016-12-31'],
                  ['2014-12-31', '2017-12-31'], ['2015-12-31', '2018-12-31'], ['2016-12-31', '2019-12-31'], ['2017-12-31', '2020-12-31'],
                  ['2018-12-31', '2021-12-31'], ['2019-12-31', '2022-12-31']]
    
    output = calcReturns(df_daily, date_pairs)
    calcExcess(output)

    # add hardcoded names
    era_names = ['Full Period', 
                 '2011+', 'GFC', '2018', 'Into COVID', 'Out of COVID', '2022',
                 '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018',
                 '2019', '2020', '2021', '2022', '2023 YTD',
                 '2011-2013', '2012-2014', '2013-2015', '2014-2016', '2015-2017', '2016-2018', '2017-2019', '2018-2020', '2019-2021', '2020-2022']
    
    output.insert(0, 'Eras', era_names)

    return output

def transformSold(df_daily, df_sold):
    # calculate performance
    df_sold['Holding Period (Y)'] = (df_sold['Sell Date'] - df_sold['Buy Date']) / 365.25
    df_sold['Security Performance'] = (df_sold['Sell Price'] / df_sold['Buy Price']) - 1
    #df_sold['Security Performance Ann'] = (1 + df_sold['Security Performance']) ** (1 / df_sold['Holding Period (Y)'] ) - 1

    # convert date column types
    df_sold['Sell Date'] = df_sold['Sell Date'].dt.strftime('%Y-%m-%d')
    df_sold['Buy Date'] = df_sold['Buy Date'].dt.strftime('%Y-%m-%d')

    # add benchmark performances
    date_pairs = list(zip(df_sold['Buy Date'],df_sold['Sell Date']))
    temp = calcReturns(df_daily, date_pairs)

    temp['Start Date'] = temp['Start Date'].dt.strftime('%Y-%m-%d')
    temp['End Date'] = temp['End Date'].dt.strftime('%Y-%m-%d')
    
    output = df_sold.merge(temp, how='left', left_on=['Buy Date', 'Sell Date'], right_on=['Start Date','End Date'])

    # drop columns (TERRIBLE, DONT CALCULATE THEM IN FIRST PLACE)
    output.drop(['Sim Start Val', 'Sim End Val',
                 'SP5E Start Val', 'SP5E End Val',
                 'R3V Start Val', 'R3V End Val',
                 'SP5 Start Val', 'SP5 End Val'], axis=1, inplace=True)
    
    output['Empty5'] = None
    output['Excess of Portfolio'] = output['Security Performance'] - output['Sim Returns']
    output['Excess of SP5E'] = output['Security Performance'] - output['SP5E Returns']
    output['Excess of R3V'] = output['Security Performance'] - output['R3V Returns']
    output['Excess of SP5'] = output['Security Performance'] - output['SP5 Returns']

    #output['Excess of Portfolio Ann'] = output['Security Performance Ann'] - output['Sim Portfolio Returns Ann']
    #output['Excess of SP5E Ann'] = output['Security Performance Ann'] - output['SP5E Portfolio Returns Ann']
    #output['Excess of R3V Ann'] = output['Security Performance Ann'] - output['R3V Portfolio Returns Ann']
    #output['Excess of SP5 Ann'] = output['Security Performance Ann'] - output['SP5 Portfolio Returns Ann']

    return output