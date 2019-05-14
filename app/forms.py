from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class LoanForm(FlaskForm):
    institution = StringField('institution', validators=[DataRequired()])
    career = StringField('career', validators=[DataRequired()])
    gender = StringField('gender', validators=[DataRequired()])
    race = StringField('race', validators=[DataRequired()])
    dependency = StringField('dependency', validators=[DataRequired()])
    income = IntegerField('income', validators=[DataRequired()])
    cost = IntegerField('cost of attendance', validators=[DataRequired()])
    expected = IntegerField('estimated family contribution', validators=[DataRequired()])
    actual = IntegerField('real family contribution', validators=[DataRequired()])
