from bs4 import BeautifulSoup
import urllib.request
from urllib.request import Request, urlopen

MONTHLY_PRICES_URL = "https://www.indexmundi.com/commodities/?commodity=pork&months=360"
PORK_FUTURES_URL = "http://www.cmegroup.com/trading/agricultural/livestock/lean-hogs.html"
CPI_URL = "http://www.usinflationcalculator.com/inflation/consumer-price-index-and-annual-percent-changes-from-1913-to-2008/"

MONTH_TO_INT = {'jan':1, 'feb':2, 'mar':3, 'apr':4, 'may':5, 'jun':6, 'jul':7, 'aug':8,
                'sep':9, 'oct':10, 'nov':11, 'dec':12}

MCRIB_DATES = ['oct 1989', 'may 1990', 'jun 1990', 'jul 1990', 'aug 1990',
               'may 1991', 'jun 1991', 'jul 1991', 'aug 1991',
               'feb 1992', 'mar 1992', 'may 1993', 'jun 1993', 'jul 1993', 'aug 1993',
               'jun 1994', 'jul 1994', 'nov 2004', 'oct 2006', 'oct 2007', 'oct 2008',
               'nov 2010', 'dec 2010', 'dec 2012', 'oct 2015', 'nov 2015', 'dec 2015',
               'jan 2016']

"""
Helper method for converting the date to a float
"""
def dateToFloat(date):
    month = date[:3]
    year = date[4:]
    monthInt = MONTH_TO_INT[month.lower()]
    monthDec = monthInt / 12
    return float(year) + monthDec

"""
Prices are already adjusted for inflation, the getCPI function has been left in for potential future
utility. It is not strictly necessary for the calculation of historic prices
"""
class PorkPrices():
    historicPrices = []
    futurePrices = []
    combinedPrices = []
    monthlyCPI = {}

    def __init__(self):
        #self.monthlyCPI = self.getCPI()
        self.historicPrices = self.getHistoric()
        self.futurePrices = self.getFuture()
        self.combinedPrices = self.combinePrices()

    def getCPI(self):
        CPIDict = {}
        with urllib.request.urlopen(CPI_URL) as response:
            html = response.read()
        soup = BeautifulSoup(html, 'lxml')
        CPITable = soup.findAll('table')
        CPITable = CPITable[0]
        CPIYears = CPITable.findAll('tr')

        CPIYears = CPIYears[2:]
        for row in CPIYears:
            year = int(row.findAll('strong')[0].text)
            if (year >= 1987):
                months = row.findAll('td')
                del months[0]
                for i, month in enumerate(months):
                    monthInt = i + 1
                    try:
                        dateFloat = float(year) + monthInt/12
                        CPIDict[dateFloat] = float(month.text)/100
                    except ValueError:
                        pass

        return CPIDict

    def getHistoric(self):
        with urllib.request.urlopen(MONTHLY_PRICES_URL) as response:
            html = response.read()
        soup = BeautifulSoup(html, 'lxml')
        priceTable = soup.find(id="gvPrices")
        priceData = []
        priceRows = priceTable.findAll('tr')
        for index, row in enumerate(priceRows):
            priceData.append([])
            cols = row.findAll('td')
            for col in cols:
                priceData[index].append(col.text)

        curTrend = 0

        del priceData[0]
        #Replaces percent change with a trend variable
        for month in priceData:
            month[1] = float(month[1])
            month[2] = curTrend
            curTrend += 1

        return priceData

    def getFuture(self):
        req = Request(
            PORK_FUTURES_URL,
            headers={'User-Agent': 'Mozilla/5.0'})
        html = urlopen(req).read()
        soup = BeautifulSoup(html, 'lxml')
        priceTable = soup.find(id="quotesFuturesProductTable1")
        priceTable = priceTable.find('tbody')
        priceData = []
        priceRows = priceTable.findAll('tr')
        for index, row in enumerate(priceRows):
            priceData.append([])
            date = row.find('span').text
            price = row.findAll('td')[4].text
            try:
                conPrice = float(price)
                priceData[index].append(date)
                priceData[index].append(conPrice)
            except:
                del priceData[-1]

        return priceData

    def combinePrices(self):
        combined = self.historicPrices.copy()
        trend = combined[-1][2] + 1
        for price in self.futurePrices:
            price.append(trend)
            combined.append(price)
            trend += 1

        return combined