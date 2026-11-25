from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, SelectField, DateField
from wtforms.validators import DataRequired, Length, Email, equal_to, NumberRange
from datetime import date

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=5,max=20)])
    email = StringField("Email", validators= [DataRequired(),Email()])
    password = StringField("Passward", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), equal_to("password", message= "Password must match") ])
    submit = SubmitField("Register")


class LoginForm(FlaskForm): 
    email = StringField("Email", validators= [DataRequired(),Email()])
    password = PasswordField("Passward", validators=[DataRequired()])
    submit = SubmitField("Login")

class ExpenseForm(FlaskForm):
    description = StringField("Description", validators=[DataRequired(), Length(max=100)])
    amount = FloatField("Amount", validators=[DataRequired(),NumberRange(min=0.01, message="Amount should be above 0.01")])
    ch = [
        ('Food','Food'),('Travel','Travel'),('Shopping','Shopping'),('Health','Health'),('Entertainment','Entertainment'),('Bills','Bills'),('Others','Others')]
    category = SelectField("Category", choices=ch, validators=[DataRequired()])
    #date = DateField("Expense Date", format="%y-%m-%d", default=date.today, validators=[DataRequired()])
    submit = SubmitField('Add Expenses')
   