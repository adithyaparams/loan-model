from flask import render_template, flash, redirect, request
from app import app, ge, scorecard, occupation
from app.forms import LoanForm
import pandas as pd
import sys
import models

def college_score(institution):
    debtToEarnings = pd.Series.item(ge[ge['Institution Name'] == institution.upper()]['Debt-to-Earnings Annual Rate']) #22.5

    defaultRate = pd.Series.item(scorecard[scorecard['INSTNM'] == institution]['CDR3']) #.00699
    federalLoanStudents = pd.Series.item(scorecard[scorecard['INSTNM'] == institution]['PCTFLOAN']) #.0355
    averageCost = pd.Series.item(scorecard[scorecard['INSTNM'] == institution]['COSTT4_A']) #64400
    medianDebt = pd.Series.item(scorecard[scorecard['INSTNM'] == institution]['GRAD_DEBT_MDN']) #6100

def personal_score(collegeScore, career, income, race, gender, efc):
    personalIncome = pd.Series.item(occupation[occupation['OCC_TITLE'] == career]['A_MEAN'].iloc[[0]])
    variations = {'White':{'Male':1.11945,'Female':0.922821},
                    'African American':{'Male':0.838333,'Female':0.756954},
                    'Asian':{'Male':1.428603,'Female':1.102105},
                    'Hispanic':{'Male':0.796935,'Female':0.704974},
                    'Other':{'Male':1,'Female':0.8}}
    realIncome = personalIncome * variations[race][gender]
    income = int(income)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/types')
def types():
    return render_template('types.html')

@app.route('/calc', methods=['GET', 'POST'])
def calc():
    form = LoanForm()
    if request.method == 'POST':
        institution=request.form['institution']
        career=request.form['career']
        income=request.form['income']
        race=request.form['race']
        gender=request.form['gender']
        cost=int(request.form['cost'])
        expected=int(request.form['expected'])
        actual=int(request.form['actual'])
        dependency=request.form['dependency']
        dependency = True if dependency == 'Dependent' else False
    loans = {}
    loans_length = len(loans)
    if form.validate_on_submit():
        loans = models.loan_division((expected-actual), True, 4, dependency)
        loans_length = len(loans)
    return render_template('calc.html', form=form, loans=loans, loans_length=loans_length)
