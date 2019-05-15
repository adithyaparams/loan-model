from flask import render_template, flash, redirect, request
from app import app, ge, scorecard, occupation
from app.forms import LoanForm
import pandas as pd
from operator import add
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

def consolidate_debt(loan_dist, type, browser, inputs):
    payments = [0,0]
    monthly = 0
    total_interest = 0
    balance = 0
    for key, loans in loan_dist.items():
        if type == 'federal':
            payments = models.repayment_plan(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], loans['Subsidized'], 5.05, 10, payments[0])
            monthly += payments[0]
            total_interest += payments[1]
            balance += loans['Subsidized']
            payments = models.repayment_plan(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], loans['Unsubsidized'], 5.05, 10, payments[0])
            monthly += payments[0]
            total_interest += payments[1]
            balance += loans['Unsubsidized']
        if type == 'private':
            payments = models.repayment_plan(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], loans['Private'], 7, 10, payments[0])
            monthly += payments[0]
            total_interest += payments[1]
            balance += loans['Private']
    return [monthly, total_interest, balance]

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
        eligibility=request.form['eligibility']
        college_term=int(request.form['term'])
        family_size=int(request.form['family'])
        cost=int(request.form['cost'])
        expected=int(request.form['expected'])
        actual=int(request.form['actual'])
        dependency=request.form['dependency']
        dependency = True if dependency == 'Dependent' else False
        eligibility = True if eligibility == 'Eligible' else False

    loans = {}
    if not len(loans) > 0:
        loans_length = len(loans)
        ibr_info, icr_info, paye_info, repaye_info = [0]*4

    if form.validate_on_submit():
        all_loans = models.loan_division((expected-actual), eligibility, college_term, dependency)
        loans = all_loans[1]
        loans_length = len(loans)

        browser = models.open_chrome()
        inputs = models.open_loan_payment_calc(browser)
        federal_loans = consolidate_debt(all_loans[0], 'federal', browser, inputs)
        private_loans = consolidate_debt(all_loans[0], 'private', browser, inputs)
        total = list(map(add, federal_loans, private_loans))

        personal_income = pd.Series.item(occupation[occupation['OCC_TITLE'] == career]['A_MEAN'].iloc[[0]])
        inputs = models.open_income_based_calc(browser, 'ibr')
        ibr_info = models.income_based_plan(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5], inputs[6], inputs[7],
                                        personal_income, family_size, 3, federal_loans[2], federal_loans[0], 5.05, inputs[8])
        inputs = models.open_income_based_calc(browser, 'icr')
        icr_info = models.income_based_plan(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5], inputs[6], inputs[7],
                                        personal_income, family_size, 3, federal_loans[2], federal_loans[0], 5.05, inputs[8])
        inputs = models.open_paye_calc(browser, 'paye')
        paye_info = models.paye_plan(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5], inputs[6],
                            personal_income, family_size, 2, federal_loans[2], federal_loans[0], 5.05, inputs[7])
        inputs = models.open_paye_calc(browser, 'repaye')
        repaye_info = models.paye_plan(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5], inputs[6],
                        personal_income, family_size, 2, federal_loans[2], federal_loans[0], 5.05, inputs[7])
        browser.close()

        for info in [ibr_info, icr_info, paye_info, repaye_info]:
            for i in info:
                print(i)

    return render_template('calc.html', form=form, loans=loans, ibr_info=ibr_info, icr_info=icr_info,
                                paye_info=paye_info, repaye_info=repaye_info, loans_length=loans_length)
