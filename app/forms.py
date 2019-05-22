from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class LoanForm(FlaskForm):
    career = StringField('career', validators=[DataRequired()])
    # gender = StringField('gender', validators=[DataRequired()])
    eligibility = StringField('eligibility', validators=[DataRequired()])
    term = IntegerField('term', validators=[DataRequired(message="Please enter a college term."), NumberRange(min=1, max=12, message='Length of college term must be between 1 and 12 years.')])
    family = IntegerField('family', validators=[DataRequired(message="Please enter a family size."), NumberRange(min=1, max=8, message='Family size must be between 1 and 8 members.')])
    # race = StringField('race', validators=[DataRequired()])
    dependency = StringField('dependency', validators=[DataRequired()])
    actual = IntegerField('real family contribution', validators=[DataRequired(message="Please enter an estimated annual student loan burden."), NumberRange(min=1, message='Students must take on a positive loan burden.')])
