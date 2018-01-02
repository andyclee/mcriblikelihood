import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LogisticRegression

from preprocessing import PreprocessedData

preprocessed = PreprocessedData(5)

#PLOTS
plt.plot(preprocessed.years, preprocessed.prices, color='g')
for i in range(len(preprocessed.mcrib)):
    if (preprocessed.mcrib.iat[i]):
        mcribYear = preprocessed.years.iat[i]
        plt.axvspan(mcribYear, mcribYear + 1/12, facecolor='r', alpha=0.5)

plt.show()

lr = LogisticRegression()
lr = lr.fit(preprocessed.independentVars, preprocessed.dependentVars)

"""
Score: 0.920903954802
"""
#print(lr.score(preprocessed.independentVars, preprocessed.dependentVars))

predictPrices = [71.775, 75.650, 80.000, 83.925, 83.825]
predictPrices = pd.Series(predictPrices)
year = 2018 + 2/12
price = predictPrices.rolling(center=True, window=5).mean()[2]
predictData = {'year':[year], 'price':[price], 'trend':[356]}
predictData = pd.DataFrame(data=predictData)
prediction = lr.predict_proba(predictData)
print(lr.classes_)
print(prediction)