from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,SelectField
from wtforms.validators import DataRequired
from app import db
class Citychoice(FlaskForm):
    # city = StringField('选择你所在的城市', validators=[DataRequired()])
    city = SelectField('选择你所在的城市 :', validators=[DataRequired()], choices=[('北京','北京'),('深圳', '深圳'),('广州','广州'),('南京','南京'),])
    submit = SubmitField('确认')