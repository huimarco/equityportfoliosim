# import libraries
import numpy as np
from datetime import datetime, timedelta

# Signal class
class Signal:
    def __init__(self, sourcedatenam, source, name, signaldate, expirydate, pricelast, pricedata):
        self.sourcedatenam = sourcedatenam
        self.source = source
        self.name = name
        self.signaldate = signaldate
        self.expirydate = expirydate

        self.pricelast = pricelast
        self.pricedata = iter(pricedata)

        self.priceprev = next(self.pricedata, None)
        self.pricenow = next(self.pricedata, None)
        self.pricenext = next(self.pricedata, None)

        self.age = 0
        self.growth = 0
        self.value = 0

        self.buydate = signaldate + timedelta(days=5)
        self.buyprice = self.pricenow

    # function to print position details
    def display(self):
        print(self.sourcedatenam, '   pricelast:', str(self.pricelast), '   priceprev/now/next:', str(self.priceprev), str(self.pricenow), str(self.pricenext), '   growth:', str(self.growth), '   val:', str(self.value))

    # function to add one to age
    def ageOneDay(self):
        self.age += 1

    # function to set pricenow based on value
    def setPrice(self, value):
        self.pricenow = value

    # function to set value based on value
    def setVal(self, value):
        self.value = value

    def updateMonthlyPrice(self):
        self.priceprev = self.pricenow
        self.pricenow = self.pricenext
        self.pricenext = next(self.pricedata, None)

    # function to recalculate value of the position
    def updateMonthlyVal(self):
        self.growth = (self.pricenow - self.priceprev) / self.priceprev
        self.value *= (1 + self.growth)

# Portfolio class (contains signals)
class Portfolio:
    def __init__(self, cash):
        self.cash = cash
        self.signallist = []

    # print each signal in portfolio
    def display(self):
        for signal in self.signallist:
            signal.display()

    # return the total value of portofolio (cash included)
    def getTotalValue(self):
        signal_values = sum(signal.value for signal in self.signallist)
        return signal_values + self.cash
    
    # return the number of signals in portfolio
    def getSize(self):
        return len(self.signallist)
    
    # return the age of oldest signal
    def getMaxAge(self):
        if not self.signallist:
            return None
        ages = np.array([signal.age for signal in self.signallist])
        ages_max = np.max(ages)
        return  ages_max
    
    # return the age of oldest signal
    def getAvgAge(self):
        if not self.signallist:
            return None
        ages_sum = np.array([signal.age for signal in self.signallist])
        ages_avg = np.mean(ages_sum)
        return ages_avg
    
    # function to buy signal
    def buySignal(self, newsig):
        # return error if new stock value is greater than portfolio value
        if newsig.value > self.getTotalValue():
            raise ValueError('Not enough funds!')
        
        # if cash is not enough
        if self.cash < newsig.value:
            cash_needed = newsig.value - self.cash
            self.cash = 0

            # loop through signals
            for signal in self.signallist:
                if cash_needed <= 0:
                    break
                cash_to_use = min(cash_needed, signal.value)
                signal.value -= cash_to_use
                cash_needed -= cash_to_use

            # remove sold out stocks from portfolio
            self.signallist = [newsig for newsig in self.signallist if newsig.value > 0]

        # if cash is enough
        else:
            self.cash -= newsig.value

        # add new signal to portfolio
        self.signallist.append(newsig)

    # function to buy each position in the datafrane
    def buyFromDfRow(self, df_row, value):
        sourcedatenam = df_row['SourceDateNam']
        source = df_row['Source']
        name = df_row['Name and Ticker']
        signaldate = df_row['Signal Date to Use']
        expirydate = df_row['Last Pricing Date']
        pricelast = df_row['Price on Last Date']
        pricedata = df_row.iloc[10:].values
        newsig = Signal(sourcedatenam, source, name, signaldate, expirydate, pricelast, pricedata)
        newsig.setVal(value)
        self.buySignal(newsig)

    # function to buy each position in the datafrane
    def buyFromDf(self, df, value):
        for index, row in df.iterrows():
            self.buyFromDfRow(row, value)
    
    # function to update all prices of all signals
    def updateMonthlyPrice(self):
        for signal in self.signallist:
            signal.updateMonthlyPrice()

    # function to update all values of all signals
    def updateMonthlyVal(self):
        for signal in self.signallist:
            signal.updateMonthlyVal()

    # function to check for positions that lost pricing data during the month
    def dumpExpired(self):
        for signal in self.signallist:
            if signal.pricenext == 0:
                self.cash += signal.value 
                signal.value = 0
                
        # remove sold out stocks from portfolio
        self.signallist = [signal for signal in self.signallist if signal.value > 0]

    # function to add one year to all signals
    def ageOneDay(self):
        for signal in self.signallist:
            signal.ageOneDay()