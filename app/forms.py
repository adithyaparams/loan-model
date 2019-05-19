from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField
from wtforms.validators import InputRequired, NumberRange

class LoanForm(FlaskForm):
    career = StringField('career', validators=[InputRequired()])
    # gender = StringField('gender', validators=[InputRequired()])
    eligibility = StringField('eligibility', validators=[InputRequired()])
    term = IntegerField('term', validators=[InputRequired(), NumberRange(min=1, max=12, message='Length of college term must be between 1 and 12 years')])
    family = IntegerField('family', validators=[InputRequired(), NumberRange(min=1, max=8, message='Family size must be between 1 and 8 members')])
    # race = StringField('race', validators=[InputRequired()])
    dependency = StringField('dependency', validators=[InputRequired()])
    actual = IntegerField('real family contribution', validators=[InputRequired(), NumberRange(min=1, message='Students must take on a positive loan burden')])
