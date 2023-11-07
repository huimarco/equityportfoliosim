import pandas as pd
from datetime import datetime, timedelta
from data_structures import Portfolio
from portfolio_sim_helpers import transformDaily, getMonthly, calcPerf

def runSim(df_newsig, df_sp500, start_date, end_date, buy_pcnt):
    # convert the date strings to datetime objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # define the step interval (1 day in this case)
    step = timedelta(days=1)

    # calculate the number of days between the start and end dates
    num_days = (end_date - start_date).days + 1

    # set up portfolio
    my_portfolio = Portfolio(cash=100)

    # create empty dataframes to store porfolio and summary data
    daily_data = []
    portfolio_data = []
    sold_data = []
    daily_columns = ['Date', 'Cash', 'Portfolio Value', 'Positions Count', 'Position Max Age', 'Position Average Age', 'New Position Count']
    portfolio_columns = ['Date', 'SourceDateNam', 'Source', 'Name', 'Signal Date', 'Last Pricing Date', 'Last Price', 'Previous Price', 'Current Price', 'Next Price','Growth','Value', 'Age']
    sold_columns = ['Sell Date','Buy Date', 'Buy Price', 'Sell Price', 'Amount']

    # loop through the dates using a for loop and range
    for i in range(num_days):
        # getting dates
        current_date = start_date + i * step
        five_days_ago = current_date - timedelta(days=5)

        # status update
        print(current_date.strftime("%Y-%m-%d"))

        # update ages, prices, and values
        my_portfolio.ageOneDay()
        my_portfolio.updateMonthlyPriceVal()

        # dump expired positions
        my_portfolio.dumpExpired()

        # grab new signals
        new_signals = df_newsig[df_newsig['Signal Date to Use'] == five_days_ago]
        buy_size = my_portfolio.getTotalValue() * buy_pcnt
        my_portfolio.buyFromDf(new_signals, buy_size)

        # collect sold signal data
        solddate = current_date
        newlysold = [[solddate] + sublist for sublist in my_portfolio.soldsigs]
        sold_data.extend(newlysold)
        my_portfolio.soldsigs.clear()

        # collect portfolio holdings and summary df data then append to data list
        portfolio_iter_data = [
            {
                'Date': current_date, 'SourceDateNam': signal.sourcedatenam, 'Source': signal.source, 
                'Name': signal.name, 'Signal Date': signal.signaldate, 'Last Pricing Date': signal.expirydate,
                'Last Price': signal.pricelast, 'Previous Price': signal.priceprev, 'Current Price': signal.pricenow,
                'Next Price': signal.pricenext, 'Growth': signal.growth, 'Value': signal.value, 'Age': signal.age
            }
            for signal in my_portfolio.signallist
        ]

        daily_iter_data = [
            {
                'Date': current_date, 'Cash': my_portfolio.cash, 'Portfolio Value': my_portfolio.getTotalValue(), 
                'Positions Count': my_portfolio.getSize(), 'Position Max Age': my_portfolio.getMaxAge(), 
                'Position Average Age': my_portfolio.getAvgAge(), 'New Position Count': len(new_signals)
            }
        ]

        portfolio_data.extend(portfolio_iter_data)
        daily_data.extend(daily_iter_data)

    # convert data lists to dataframe
    daily_df = pd.DataFrame(daily_data, columns=daily_columns)
    portfolio_df = pd.DataFrame(portfolio_data, columns=portfolio_columns)
    sold_df = pd.DataFrame(sold_data, columns=sold_columns)

    # add summary stats to porfolio; add S&P data to summary
    portfolio_df = pd.merge(portfolio_df, daily_df, on='Date', how='left')

    # make data transformations to daily_df
    daily_df = transformDaily(daily_df, df_sp500)

    # get monthly data
    monthly_df = getMonthly(daily_df)

    # calculate returns for different time periods
    returns_df = calcPerf(daily_df)

    return portfolio_df, daily_df, monthly_df, returns_df, sold_df