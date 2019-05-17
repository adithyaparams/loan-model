from sympy.solvers import solve
from sympy import Symbol

variations = {'White':{'Male':1.11945,'Female':0.922821},
              'African American':{'Male':0.838333,'Female':0.756954},
              'Asian':{'Male':1.428603,'Female':1.102105},
              'Hispanic':{'Male':0.796935,'Female':0.704974},
              'Other':{'Male':1,'Female':0.8}}

mort_rates = [5.367, 4.821, 4.391, 4.177, 4.000, 3.778]
rate_range = [4.07, 13.25] #fixed rate

def salary_proj_old(avg):
    r = 0.004
    multiplier = 1.1 
    start = 0.7*avg
    s_max = multiplier * float(avg)
    out = []
    for t in range(0, 31):
        denom = 1.00 + (s_max / (float(start) - 1))**(-r*s_max*t)
        out.append(s_max/denom)
    
    foravg = 0.0
    for i in range(4,14):
        foravg+=(out[i+1]-out[i])
    foravg/=10
    
    return [out, foravg]
    
def salary_proj(avg, gender, race, term=10):
    
    career = []
    coef = variations[race][gender]
    for i in range(0, 30):
        career.append(avg*coef)
    for i in range(0, 5):
        career[i]*=(510.5714/873.0476)
    return career

print(salary_proj(60000, 'Male', 'White'))

def pred_interest(creditscore):
    if creditscore >= 620 and creditscore < 780:
        new = int((creditscore - 620)/20)
        multiplier = (mort_rates[new] - mort_rates[-1])/(mort_rates[0] - mort_rates[-1])
        rate = multiplier*(rate_range[1] - rate_range[0]) + rate_range[0]
    elif creditscore >= 780:
        rate = rate_range[0]
    else:
        rate = rate_range[1]
        
    return rate
    
def recur(n, principal, const, monthly):
    if n == 1:
        return (principal*const - monthly)
    elif n>1:
        return (recur(n-1, principal, const, monthly)*const - monthly)
    
def monthly_payment(principal, rate, term=10):

    monthly = Symbol('monthly')
    const = (1 + rate/365)**(365.0/12)
    out = solve(recur(term*12, principal, const, monthly), monthly)[0]
    return [out, out*12*term - principal, out*12*term]
        