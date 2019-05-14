from flask import Flask
from app.config import Config
import pandas as pd

app = Flask(__name__)
app.config.from_object(Config)
ge = pd.read_excel('app/static/ge.xls')
scorecard = pd.read_csv('app/static/scorecard.csv')
occupation = pd.read_excel('app/static/occupation.xlsx')

from app import routes
