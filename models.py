from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.expected_conditions import _find_element
from selenium.webdriver.common.keys import Keys
import os, itertools, copy
import sys

def salary_proj(avg):
    r = 0.004
    multiplier = 1.1
    start = 0.7*avg
    s_max = multiplier * float(avg)
    out = []
    for t in range(0, 31):
        denom = 1.00 + (s_max / (float(start) - 1))**(-r*s_max*t)
        out.append(s_max/denom)
    return out

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

def open_chrome():
    opts = Options()
    # opts.add_argument('headless')
    chrome_options = Options()
    chrome_options.binary_location = GOOGLE_CHROME_BIN
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    browser = Chrome(executable_path=CHROMEDRIVER_PATH), options=opts, chrome_options=chrome_options)
    return browser

def open_loan_payment_calc(browser):
    browser.get('https://studentloanhero.com/calculators/student-loan-payment-calculator/')
    balance = browser.find_element_by_xpath("//input[@data-field='amount']")
    percent = browser.find_element_by_xpath("//input[@data-field='rate']")
    term = browser.find_element_by_xpath("//input[@data-field='years']")
    button = browser.find_element_by_xpath("//button[@class='  blue-color default-button calcs-describe-ad-btn results-button opt  null']")
    return [browser, balance, percent, term, button]

def repayment_plan(browser, balance, percent, term, button, balance_input, percent_input, term_input, text_before):
    length = len(balance.get_attribute('value'))                                    # clear values
    balance.send_keys(length * Keys.BACKSPACE)
    length = len(percent.get_attribute('value'))
    percent.send_keys(length * Keys.BACKSPACE)
    length = len(term.get_attribute('value'))
    term.send_keys(length * Keys.BACKSPACE)

    balance.send_keys(str(balance_input))                                           # input values
    percent.send_keys(str(percent_input))
    term.send_keys(str(term_input))
    button.click()
                                                                                    # scrape output
    WebDriverWait(browser, 10).until(text_to_change((By.XPATH, "//div[@class='calc-opt-card animated-left']/h4/span"), text_before))
    monthly = browser.find_element_by_xpath("//div[@class='calc-opt-card animated-left']/h4/span").text
    monthly = int(monthly[1:].replace(',',''))
    interest = browser.find_element_by_xpath("//div[@class='calc-opt-card animated-right']/h4/span").text
    interest = int(interest[1:].replace(',',''))
    return [monthly, interest]

def open_income_based_calc(browser, plan):
    sites = {'ibr': 'https://studentloanhero.com/calculators/student-loan-income-based-repayment-calculator/',
                'icr': 'https://studentloanhero.com/calculators/income-contingent-repayment-calculator/'}
    browser.get(sites[plan])
    income = browser.find_element_by_xpath("//input[@data-field='agi']")
    dropdown = browser.find_elements_by_xpath('//div[@class="dropdown btn-group"]')
    family_size = dropdown[0]
    income_growth_rate = browser.find_element_by_xpath("//input[@data-field='ibr_aig']")
    old_loans = dropdown[2]
    total_debt = browser.find_element_by_xpath("//input[@data-field='total_debt']")
    monthly_payment = browser.find_element_by_xpath("//input[@data-field='monthly_payment']")
    interest_rate = browser.find_element_by_xpath("//input[@data-field='rate']")
    return [browser, income, family_size, income_growth_rate, old_loans, total_debt, monthly_payment, interest_rate, plan]

def income_based_plan(browser, income, family_size, income_growth_rate, old_loans, total_debt, monthly_payment, interest_rate,
                        income_input, family_size_input, income_growth_rate_input, total_debt_input, monthly_payment_input, interest_rate_input, plan):
    length = len(income.get_attribute('value'))                                     # clear values
    income.send_keys(length * Keys.BACKSPACE)
    length = len(income_growth_rate.get_attribute('value'))
    income_growth_rate.send_keys(length * Keys.BACKSPACE)
    length = len(total_debt.get_attribute('value'))
    total_debt.send_keys(length * Keys.BACKSPACE)
    length = len(monthly_payment.get_attribute('value'))
    monthly_payment.send_keys(length * Keys.BACKSPACE)
    length = len(interest_rate.get_attribute('value'))
    interest_rate.send_keys(length * Keys.BACKSPACE)

    income.send_keys(str(income_input))                                             # input values
    family_size.click()
    li = family_size.parent.find_elements_by_xpath("//li[@role='presentation']")
    li[int(family_size_input)-1].click()
    income_growth_rate.send_keys(str(income_growth_rate_input))
    old_loans.click()
    li[14].click()
    total_debt.send_keys(str(total_debt_input))
    monthly_payment.send_keys(str(monthly_payment_input))
    interest_rate.send_keys(str(interest_rate_input))

    WebDriverWait(browser, 10).until(text_to_change((By.XPATH, "//td/span"),        # scrape output
        browser.find_element_by_xpath("//td/span").text))
    table = browser.find_elements_by_xpath("//td")
    values = [item.text for item in table]
    tuple_values = list(grouper(4, values))
    split_values = []
    for x in tuple_values:
        split_values.append(list(x))
    split_values = [['', 'Original', plan.upper(), 'Savings']] + split_values[:5]
    split_values[1][0] = 'Monthly payments'
    return split_values

def open_paye_calc(browser, plan):
    sites = {'paye': 'https://studentloanhero.com/calculators/pay-as-you-earn-calculator/',
                'repaye': 'https://studentloanhero.com/calculators/student-loan-revised-pay-as-you-earn-calculator/'}
    browser.get(sites[plan])
    income = browser.find_element_by_xpath("//input[@data-field='agi']")
    dropdown = browser.find_elements_by_xpath('//div[@class="dropdown btn-group"]')
    family_size = dropdown[0]
    income_growth_rate = browser.find_element_by_xpath("//input[@data-field='ibr_aig']")
    total_debt = browser.find_element_by_xpath("//input[@data-field='total_debt']")
    monthly_payment = browser.find_element_by_xpath("//input[@data-field='monthly_payment']")
    interest_rate = browser.find_element_by_xpath("//input[@data-field='rate']")
    return [browser, income, family_size, income_growth_rate, total_debt, monthly_payment, interest_rate, plan]

def paye_plan(browser, income, family_size, income_growth_rate, total_debt, monthly_payment, interest_rate,
                income_input, family_size_input, income_growth_rate_input, total_debt_input, monthly_payment_input, interest_rate_input, plan):
    length = len(income.get_attribute('value'))                                     # clear values
    income.send_keys(length * Keys.BACKSPACE)
    length = len(income_growth_rate.get_attribute('value'))
    income_growth_rate.send_keys(length * Keys.BACKSPACE)
    length = len(total_debt.get_attribute('value'))
    total_debt.send_keys(length * Keys.BACKSPACE)
    length = len(monthly_payment.get_attribute('value'))
    monthly_payment.send_keys(length * Keys.BACKSPACE)
    length = len(interest_rate.get_attribute('value'))
    interest_rate.send_keys(length * Keys.BACKSPACE)

    income.send_keys(str(income_input))                                             # input values
    family_size.click()
    li = family_size.parent.find_elements_by_xpath("//li[@role='presentation']")
    li[int(family_size_input)-1].click()
    income_growth_rate.send_keys(str(income_growth_rate_input))
    total_debt.send_keys(str(total_debt_input))
    monthly_payment.send_keys(str(monthly_payment_input))
    interest_rate.send_keys(str(interest_rate_input))

    WebDriverWait(browser, 10).until(text_to_change((By.XPATH, "//td/span"),        # scrape output
        browser.find_element_by_xpath("//td/span").text))
    table = browser.find_elements_by_xpath("//td")
    values = [item.text for item in table]
    tuple_values = list(grouper(4, values))
    split_values = []
    for x in tuple_values:
        split_values.append(list(x))
    split_values = [['', 'Original', plan.upper(), 'Savings']] + split_values[:5]
    split_values[1][0] = 'Monthly payments'
    return split_values

# browser = open_chrome()

# inputs = open_loan_payment_calc(browser)
# payments = repayment_plan(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], 10000, 5.05, 10, '$0')
# print(payments)
# payments = repayment_plan(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], 20000, 5.05, 10, payments[0])
# print(payments)

# inputs = open_income_based_calc(browser, 'paye')
# info = income_based_plan(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5], inputs[6], inputs[7], 74000, 4, 2, 180000, 1000, 5.05, inputs[8])

# inputs = open_paye_calc(browser, 'repaye')
# info = paye_plan(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5], inputs[6], 74000, 4, 2, 180000, 1000, 5.05, inputs[7])
#
# for value in info:
#     print(value)
