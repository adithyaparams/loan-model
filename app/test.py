import pandas as pd

ge = pd.read_excel('app/static/ge.xls')
scorecard = pd.read_csv('app/static/scorecard.csv')

print(pd.Series.item(ge[ge['Institution Name'] == uppercase(institution)]['Debt-to-Earnings Annual Rate'])) #22.5

print(pd.Series.item(scorecard[scorecard['INSTNM'] == institution]['CDR3']))
print(pd.Series.item(scorecard[scorecard['INSTNM'] == institution]['PCTFLOAN']))
print(pd.Series.item(scorecard[scorecard['INSTNM'] == institution]['COSTT4_A']))
print(pd.Series.item(scorecard[scorecard['INSTNM'] == institution]['GRAD_DEBT_MDN']))
