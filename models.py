from sympy.solvers import solve
from sympy import Symbol
import os, itertools, copy
import sys

class text_to_change(object):
    def __init__(self, locator, text):
        self.locator = locator
        self.text = text
    def __call__(self, driver):
        actual_text = _find_element(driver, self.locator).text
        return actual_text != self.text

def place_value(number):
    return ("{:,}".format(number))

def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)

def loan_division(annual_loan_burden, sub_eligible, college_term, dependent):
    loans = {}
    for year in range(college_term):
        loans[int(year)] = {'Subsidized':0, 'Unsubsidized':0, 'Private':0}

    if sub_eligible and dependent:
        sub_max = 23000
        unsub_max = 8000
        sub_yearly_max = [3500, 4500, 5500]
        unsub_yearly_max = [2000, 2000, 2000]
    elif not sub_eligible and dependent:
        sub_max = 0
        unsub_max = 31000
        sub_yearly_max = [0, 0, 0]
        unsub_yearly_max = [5500, 6500, 7500]
    elif sub_eligible and not dependent:
        sub_max = 23000
        unsub_max = 34500
        sub_yearly_max = [3500, 4500, 5500]
        unsub_yearly_max = [6000, 6000, 7000]
    else:
        sub_max = 0
        unsub_max = 57500
        sub_yearly_max = [0, 0, 0]
        unsub_yearly_max = [9500, 10500, 12500]

    for year in range(college_term):
        sample_burden = annual_loan_burden
        if year < 2:
            loan_index = year
        else:
            loan_index = 2

        if sample_burden <= sub_yearly_max[loan_index]:
            loans[year]['Subsidized'] = sample_burden
            sub_max -= sample_burden
        elif sample_burden > sub_yearly_max[loan_index] and sample_burden < (sub_yearly_max[loan_index] + unsub_yearly_max[loan_index]):
            loans[year]['Subsidized'] = sub_yearly_max[loan_index]
            loans[year]['Unsubsidized'] = sample_burden - sub_yearly_max[loan_index]
            sub_max -= sub_yearly_max[loan_index]
            unsub_max -= (sample_burden - sub_yearly_max[loan_index])
        elif sample_burden > (sub_yearly_max[loan_index] + unsub_yearly_max[loan_index]):
            loans[year]['Subsidized'] = sub_yearly_max[loan_index]
            loans[year]['Unsubsidized'] = unsub_yearly_max[loan_index]
            loans[year]['Private'] = sample_burden - sub_yearly_max[loan_index] - unsub_yearly_max[loan_index]
            sub_max -= sub_yearly_max[loan_index]
            unsub_max -= unsub_yearly_max[loan_index]

        if sub_max < sub_yearly_max[loan_index]:
            sub_yearly_max[loan_index] = sub_max
        if unsub_max < unsub_yearly_max[loan_index]:
            unsub_yearly_max[loan_index] = unsub_max

    text_loans = copy.deepcopy(loans)

    for l in text_loans:
        text_loans[l]['Subsidized'] = "$" + place_value(text_loans[l]['Subsidized'])
        text_loans[l]['Unsubsidized'] = "$" + place_value(text_loans[l]['Unsubsidized'])
        text_loans[l]['Private'] = "$" + place_value(text_loans[l]['Private'])

    return [loans, text_loans]

def consolidate_debt(loan_dist, type, term=10):
    payments = [0,0]
    monthly = 0
    total_interest = 0
    balance = 0
    for key, loans in loan_dist.items():
        if type == 'federal':
            payments = repayment_plan(loans['Subsidized'], .0505, term)
            monthly += payments[0]
            total_interest += payments[1]
            balance += payments[2]
            payments = repayment_plan(loans['Unsubsidized'], .0505, term)
            monthly += payments[0]
            total_interest += payments[1]
            balance += payments[2]
        if type == 'private':
            payments = repayment_plan(loans['Private'], .07, term)
            monthly += payments[0]
            total_interest += payments[1]
            balance += payments[2]
    return [monthly, total_interest, balance]

def recur(n, principal, const, monthly):
    if n == 1:
        return (principal*const - monthly)
    elif n>1:
        return (recur(n-1, principal, const, monthly)*const - monthly)

def repayment_plan(principal, rate, term=10):
    monthly = Symbol('monthly')
    const = (1 + rate/365)**(365.0/12)
    out = solve(recur(term*12, principal, const, monthly), monthly)[0]
    monthly = out
    interest = out*12*term - principal
    total = out*12*term
    return [int(monthly), int(interest), int(total)]

def salary_proj(avg, gender=1, race=1, term=10):
    variations = {'White':{'Male':1.11945,'Female':0.922821},
                  'African American':{'Male':0.838333,'Female':0.756954},
                  'Asian':{'Male':1.428603,'Female':1.102105},
                  'Hispanic':{'Male':0.796935,'Female':0.704974},
                  'Other':{'Male':1,'Female':0.8}}
    career = [0]*30
    # coef = variations[race][gender]
    coef = 1
    for i in range(5):
        career[i] = avg*(1/1.02)**(4-i)
    for i in range(5, 30):
        career[i] = avg*(1.03)**(i-4)
    return career
