from flask import Flask, url_for, redirect, render_template, flash, session
from forms import RegisterForm,ExpenseForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)

app.config['SECRET_KEY'] = "b5e75dc3b7ef1345da637b86254d7609217a5abefae25534c774e95ba68385bep"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'

db = SQLAlchemy(app)

class User(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     username = db.Column(db.String(20), unique=True, nullable=False)
     email = db.Column(db.String(100), unique=True, nullable=False )
     password = db.Column(db.String(256), nullable=False)
     expenses = db.relationship("Expense",backref= "owner", lazy=True)

     def __str__(self):
          return f"<User{self.username}>"

class Expense(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     description = db.Column(db.String(100),nullable=False)
     amount = db.Column(db.Float, nullable=False)
     category = db.Column(db.String(50), nullable=False)
     date= db.Column(db.DateTime, default=datetime.now)
     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

     def __str__(self):
               return f"<Expense{self.description}, Amount: {self.amount}>"


def check_login():
    if session.get("user_id"):
        return True
    return False

@app.route('/')
def home ():
    flash('Welcome to Expense Tracter', 'success')
    return  render_template('home.html')

@app.route('/dashboard')
def dashboard():
    if check_login():
        total = 0

        current_user = session['user_id']
        user_expenses = Expense.query.filter_by(user_id=current_user).all()

        for exp in user_expenses:
            total += exp.amount
        
        transaction_count = len(user_expenses)
        
        categories = []
        breakdown = {}
        
        for exp in user_expenses:
            categories.append(exp.category)

            if exp.category in breakdown:
                breakdown[exp.category] += exp.amount
            else:
                breakdown[exp.category] = exp.amount

        n_categories = len(set(categories))
        
        return render_template('dashboard.html', total=total, count=transaction_count, categories=n_categories, spend_by_cat=breakdown)
    else:
        flash(f'Please login to continue', "error")
        return redirect(url_for("login"))

        
@app.route('/expenses')    
def expenses():
    if check_login():
        current_user = session['user_id']
        user_expenses = Expense.query.filter_by(user_id=current_user).order_by(Expense.date.desc()).all()
        return  render_template('expenses.html', expenses = user_expenses)
    else:
            flash(f'Please login to continue', "error")
            return redirect(url_for("login"))
    

#viewing for single expense
@app.route('/expense/<int:expense_id>')
def expense_detail(expense_id):
    if check_login():
           expense = Expense.query.get_or_404(expense_id)
           if expense.user_id == session["user_id"]:
                return render_template("single_expense.html", expense=expense)
           flash("Unauthoried user!", "error")
           return redirect(url_for('expenses'))

    else:
        flash('Please login to continue', "error")
        return redirect(url_for("login"))


#deleting a specific expense
@app.route('/expenses/<int:expense_id>/delete', methods =["POST"])
def delete_expense(expense_id):
    if check_login():
        expense = Expense.query.get_or_404(expense_id)
        if expense.user_id == session["user_id"]:
            db.session.delete(expense)
            db.session.commit()
            flash(f"Expense {expense.description} for Rs. {expense.amount} deleted!", "success")
            return redirect(url_for('expenses'))

        flash("unauthorised!", "error")
        return redirect(url_for('expenses'))
    #logic for deleting the expenses
    else:
        flash(f'Please login to continue', "error")
        return redirect(url_for("login"))

    
@app.route('/add', methods= ['GET', 'POST'])
def add_expense():
    if check_login():
            form = ExpenseForm()
            if form.validate_on_submit():
                    description = form.description.data
                    amount = form.amount.data
                    category = form.category.data
                    current_user = session['user_id']

                    #save to DB
                    expense = Expense(description=description, amount=amount,
                                      category=category, user_id=current_user)
                    db.session.add(expense)
                    db.session.commit()
                    flash(f"Expense of amount Rs. {amount} for  added!", "success")
                    return redirect(url_for("expenses"))
            
            return render_template('add_expense.html',form=form)
    else:
        flash(f'Please login to continue', "error")
        return redirect(url_for("login"))
    


@app.route('/register', methods= ['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

    #vaildating if the user or email already exists
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash(f" Account with this email id already exists, try login", "error")
            return render_template('register.html', form=form)

        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash(f" account with username already exists, try new username!", "error")
            return render_template('register.html', form=form)

       #registering the user/add the user in the database
        user = User(username=username,email=email,password= generate_password_hash(password))
       #save database
        db.session.add(user)
        db.session.commit()

        flash(f"Account successful created for {username}!", "success")
        return redirect(url_for("login"))

    return  render_template('register.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
     form = LoginForm()

     if form.validate_on_submit():
         entered_email = form.email.data
         entered_password = form.password.data

         existing_user = User.query.filter_by(email=entered_email).first()
         if existing_user and check_password_hash(existing_user.password, entered_password):
                 session["user_id"] = existing_user.id
                 session["username"] = existing_user.username
                 flash(f"Welcome back, {existing_user.username}", "success")
                 return redirect(url_for("dashboard"))

         flash("Invaild email or password!!", "error")   

     return  render_template('login.html', form=form)

@app.route('/logout')
def logout():
    if check_login():
           session.clear()
           flash(f"You have been logged out!!", "success")
           return redirect(url_for('home'))
    else:
        flash(f'Please login to continue', "error")
        return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(debug=True)