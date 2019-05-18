from flask import render_template, flash, redirect, request
from app import app, occupation
from app.forms import LoanForm
import pandas as pd
from operator import add
import sys
import models

def min_max_discretionary(income_dist, family, monthly):
    elev_pov_line = [18090, 24360, 30630, 36900, 43170, 49440, 55710, 61980]
    print(income_dist[0], income_dist[9], family, file=sys.stderr)
    min = monthly*12/(income_dist[0] - elev_pov_line[family-1])
    max = monthly*12/(income_dist[9] - elev_pov_line[family-1])
    return [int(max*100), int(min*100)]

def place_value(number):
    return ("{:,}".format(number))

def stringify(num):
    return '$' + place_value(int(num))

def extended_loans(standard_loans, loan_dist):
    table = []
    eloans = models.consolidate_debt(loan_dist, 'federal', 20)
    table.append(['', 'Standard', 'Extended', 'Savings'])
    table.append(['Monthly Payments', stringify(standard_loans[0]), stringify(eloans[0]), stringify(-eloans[0]+standard_loans[0])])
    table.append(['Total Balance', stringify(standard_loans[2]), stringify(eloans[2]), stringify(-eloans[2]+standard_loans[2])])
    table.append(['Debt Forgiveness', '$0', '$0', '$0'])
    table.append(['Repayment Period', '~10yrs', '~20yrs', '-10yrs'])
    return table

def icr_loans(standard_loans, loan_dist, income, family):
    elev_pov_line = [18090, 24360, 30630, 36900, 43170, 49440, 55710, 61980]
    table = []
    eloans = models.consolidate_debt(loan_dist, 'federal', 20)
    table.append(['', 'Standard', 'ICD', 'Savings'])
    icr_monthly = (income-elev_pov_line[family])/12*.2
    table.append(['Monthly Payments', stringify(standard_loans[0]), stringify(icr_monthly), stringify(-eloans[0]+icr_monthly)])
    table.append(['Total Balance', stringify(standard_loans[2]), stringify(eloans[2]), stringify(-eloans[2]+standard_loans[2])])
    diff = eloans[2]-240*icr_monthly
    table.append(['Debt Forgiveness', '$0', stringify(diff), stringify(diff)])
    table.append(['Repayment Period', '~10yrs', '~20yrs', '-10yrs'])
    return table

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
        career=request.form['career']
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

    total = ['']*3
    plans = {'Extended':'Extended Repayment Plan', 'ICD':'Income-Driven Repayment (ICD) Plans'}
    desc = {'Extended':'If you need to make lower monthly payments over a longer period of time than under \
                plans such as the Standard Repayment Plan, then the Extended Repayment Plan may be right for you.',
                'ICD':'An income-driven repayment plan sets your monthly student loan payment at an amount that \
                is intended to be affordable based on your income and family size.'}
    text_loans = {}
    pct_range = []
    pct_range_text = ''
    if not len(text_loans) > 0:
        loans_length = len(text_loans)
        extended, icr = [0]*2

    if form.validate_on_submit():
        all_loans = models.loan_division(actual, eligibility, college_term, dependency)
        text_loans = all_loans[1]
        loans_length = len(text_loans)

        federal_loans = models.consolidate_debt(all_loans[0], 'federal')
        private_loans = models.consolidate_debt(all_loans[0], 'private')
        total_num = list(map(add, federal_loans, private_loans))
        total[0] = '$' + place_value(total_num[0])
        total[1] = '$' + place_value(total_num[1])
        total[2] = '$' + place_value(total_num[2])

        occupation_income = pd.Series.item(occupation[occupation['OCC_TITLE'] == career]['A_MEAN'].iloc[[0]])
        incomes = models.salary_proj(occupation_income, gender, race)
        pct_range = min_max_discretionary(incomes, family_size, total_num[0])
        pct_range_text = str(pct_range[0]) + "% - " + str(pct_range[1]) + "%"

        extended = extended_loans(federal_loans, all_loans[0])
        icr = icr_loans(federal_loans, all_loans[0], occupation_income, family_size)

    return render_template('calc.html', form=form, plans=plans, total=total, loans=text_loans, extended=extended, icr=icr, desc=desc,
                                pct_range=pct_range, pct_range_text=pct_range_text, loans_length=loans_length)
