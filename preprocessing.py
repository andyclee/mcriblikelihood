from datacollect import PorkPrices, dateToFloat, MCRIB_DATES
import pandas as pd

"""
PREPROCESSING
"""

def movingAverage(dataArr, numPoints):
    maData = []
    for i in range(numPoints, len(dataArr)):
        curMA = 0
        for j in range(numPoints):
            curMA += maData[i - numPoints + j]

        curMA = curMA / numPoints
        maData.append(curMA)

    return maData

class PreprocessedData():
    data = PorkPrices()
    windowSize = 0
    prices = []
    years = []
    pastYears = []
    trend = []
    mcrib = []
    independentVars = []
    dependentVars = []

    def __init__(self, window):
        self.windowSize = window
        for row in self.data.combinedPrices:
            self.years.append(row[0])
            self.prices.append(row[1])
            self.trend.append(row[2])

        self.years = pd.Series(self.years)
        self.years = self.years.apply(lambda x : x.lower())
        self.prices = self.deseasonalize(self.years, self.prices)
        self.prices = pd.Series(self.prices)
        self.trend = pd.Series(self.trend)

        self.prices = self.prices.rolling(center=True, window=self.windowSize).mean()

        #Format date for regression
        self.years = self.years.apply(dateToFloat)

        pastYears = []
        for row in self.data.historicPrices:
            pastYears.append(row[0])

        mcribArr = []
        for year in pastYears:
            if (year.lower() in MCRIB_DATES):
                mcribArr.append(1)
            else:
                mcribArr.append(0)

        self.mcrib = pd.Series(mcribArr, name="has_mcrib")
        self.dependentVars = self.mcrib

        cols = {"year": self.years, "price": self.prices, "trend": self.trend}
        self.independentVars = pd.DataFrame(data=cols)

        #Drop future values
        self.independentVars.drop(self.independentVars.index[self.dependentVars.shape[0]:], inplace=True)
        maDrops = self.windowSize // 2
        self.independentVars.drop(self.independentVars.index[:maDrops], inplace=True)
        self.years = self.independentVars['year']
        self.prices = self.independentVars['price']
        self.trend = self.independentVars['trend']
        self.dependentVars.drop(self.dependentVars.index[:maDrops], inplace=True)

    def mean(self, data):
        sum = 0
        for point in data:
            sum += point
        return sum / len(data)

    """
    Dates are expected in format of: three-letter-month year
    """
    def deseasonalize(self, dates, values):
        seasons = {}
        cycles = {}
        for idx, date in enumerate(dates):
            month = date[:3]
            year = date[4:]
            if month in seasons:
                seasons[month].append((values[idx], year))
            else:
                seasons[month] = [(values[idx], year)]

            if year in cycles:
                cycles[year].append(values[idx])
            else:
                cycles[year] = [values[idx]]

        #Get average prices per cycle
        for year, prices in cycles.items():
            cycles[year] = self.mean(prices)

        proportions = {}
        #Gets proportions for each month
        for month, prices in seasons.items():
            for price in prices:
                if month in proportions:
                    proportions[month].append(price[0] / cycles[price[1]])
                else:
                    proportions[month] = [price[0] / cycles[price[1]]]

        #Convert from proportions to indices
        for month, props in proportions.items():
            proportions[month] = self.mean(props)

        deseasonalized = []
        for idx, date in enumerate(dates):
            month = date[:3]
            deseasonalized.append(values[idx] / proportions[month])

        return deseasonalized