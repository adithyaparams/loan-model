from flask import render_template, flash, redirect, request
from app import app, occupation
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

def min_max_discretionary(income_dist, family, monthly):
    elev_pov_line = [18090, 24360, 30630, 36900, 43170, 49440, 55710, 61980]
    print(income_dist[0], income_dist[9], family, file=sys.stderr)
    min = monthly*12/(income_dist[0] - elev_pov_line[family-1])
    max = monthly*12/(income_dist[9] - elev_pov_line[family-1])
    return [int(max*100), int(min*100)]



def place_value(number):
    return ("{:,}".format(number))

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
    plans = {'IBR':'Income-Based Repayment (IBR) Plan', 'ICR':'Income-Contingent Repayment (ICR) Plan',
                'PAYE':'Pay As You Earn (PAYE) Plan', 'REPAYE':'Revised Pay As You Earn (REPAYE) Plan'}
    loans = {}
    pct_range = []
    pct_range_text = ''
    if not len(loans) > 0:
        loans_length = len(loans)
        ibr_info, icr_info, paye_info, repaye_info = [0]*4

    if form.validate_on_submit():
        all_loans = models.loan_division(actual, eligibility, college_term, dependency)
        loans = all_loans[1]
        loans_length = len(loans)

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

    return render_template('calc.html', form=form, plans=plans, total=total, loans=loans,
                                pct_range=pct_range, pct_range_text=pct_range_text, loans_length=loans_length)
