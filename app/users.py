from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from io import BytesIO
import base64
import matplotlib.pyplot as plt
from .models.purchase import Purchase
from .models.user import User
from .models.review import Review
from .models.review import Seller_Review


from flask import Blueprint
bp = Blueprint('users', __name__)

#LOGIN Form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign in')

#Login Route
@bp.route('/login', methods=['GET', 'POST'])
def login():
    #redirects user if already authenticated
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

#Registration form
class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')

#Register route
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.register(form.firstname.data,
                         form.lastname.data,
                         form.email.data,
                         form.password.data):
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

#balance route - view and edit current user's balance
@bp.route('/balance', methods = ['GET', 'POST'])
def balance():
    form = UpdateBalanceForm()
    #check to see if user is authenticated
    if current_user.is_authenticated:
        user = User.get_all(current_user.id)
        #has email, name, password, address, balance
    else:
        return redirect(url_for('users.login'))

    #when form is submitted, call update_balance and redirect to /balance
    #adding money
    if form.validate_on_submit():
        balance = user[0].balance
        amount = form.amount.data
        if form.withdraw.data:
            if amount > balance:
                flash('Insufficient funds!')
                return redirect(url_for('users.balance'))
            amount *= -1
            
        User.edit_balance(current_user.id, amount, balance)
        user = User.get_all(current_user.id)

        flash("{button}{amount}".format(amount = form.amount.data, button = "Added $" if form.add.data else "Withdrew $"))
        return render_template('balance.html', user = user, form = form, showAnimation = True)

    return render_template('balance.html', user = user, form = form, showAnimation = False)

class UpdateBalanceForm(FlaskForm):
    amount = DecimalField('Amount', validators = [])
    add = SubmitField('➕ Add')
    withdraw = SubmitField('➖ Withdraw')

#current user's account information
@bp.route('/account', methods = ['GET', 'POST'])
def account_page():
    if current_user.is_authenticated:
        user = User.get_all(current_user.id)
        #has email, name, password, address, balance
    else:
        return redirect(url_for('users.login'))
    
    return render_template('account.html', user = user)

class UpdateForm(FlaskForm):
    firstname = StringField('First Name')
    lastname = StringField('Last Name')
    email = StringField('Email')
    address = StringField('Address')
    password = PasswordField('Password')
    password2 = PasswordField(
        'Repeat Password', validators=[EqualTo('password')])
    submit = SubmitField('Update')

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')


#edit current user's account information
@bp.route('/account/edit', methods = ['GET', 'POST'])
def edit_account():
    #if not logged in, redirect
    email = ""
    if current_user.is_authenticated:
        user = User.get_all(current_user.id)
    else:
        redirect(url_for('users.login'))
    form = UpdateForm()
    if form.validate_on_submit():
        #if fields are empty, use current info
        email = form.email.data if form.email.data else user[0].email
        password = form.password.data if form.password.data else User.get_password(current_user.id)
        firstname = form.firstname.data if form.firstname.data else user[0].full_name.split(" ")[0]
        lastname = form.lastname.data if form.lastname.data else user[0].full_name.split(" ")[1]
        address = form.address.data if form.address.data else user[0].address
        full_name = firstname + " " + lastname
        #call update function to update user's information in the db
        if User.update(current_user.id, full_name, email, address, password):
            flash("Successfully updated information!")
            return redirect(url_for('users.account_page'))
        else:
            flash('hello')
    return render_template('edit_account.html', user = user, form=form)

#logout route
@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))

class SearchBarForm(FlaskForm):
    query = StringField('', validators=[DataRequired()])
    submit = SubmitField('🔍')

#search account page
@bp.route('/view_accounts', methods = ['GET', 'POST'])
def view_accounts():
    if not current_user.is_authenticated:
        redirect(url_for('users.login'))
    form = SearchBarForm()
    account, reviews, seller = None, None, None
    #after submitting, use query to retrieve information
    if form.validate_on_submit():
        account = User.get(form.query.data)
        reviews = Review.get_all_product_reviews(form.query.data)
        seller = Seller_Review.get_all_seller_reviews(form.query.data)
    
    #initial state, use current id instead
    else:
        account = User.get(current_user.id)
        reviews = Review.get_all_product_reviews(current_user.id)
        seller = Seller_Review.get_all_seller_reviews(current_user.id)
 
    return render_template('public_account.html', form = form, account = account, reviews = reviews, seller = seller)


@bp.route('/spending', methods = ['GET', 'POST'])
def spending():
    if current_user.is_authenticated:
        purchases = Purchase.get_purchases(current_user.id)
        data = {}
        for purchase in purchases:
            if purchase.category not in data:
                data[purchase.category] = purchase.unit_price_at_time_of_payment * purchase.quantity
            else:
                data[purchase.category] += purchase.unit_price_at_time_of_payment * purchase.quantity
        img = BytesIO()
        categories = list(data.keys())
        values = list(data.values())
        c = ['#2c7962', '#d38541', '#2c7962', '#d38541', '#2c7962']
        def addlabels(x,y):
            for i in range(len(x)):
                plt.text(i, y[i] + 15, '$' + str(y[i]), ha = 'center')

        fig = plt.figure(figsize = (8, 5))
        ax = plt.axes()
        ax.set_facecolor('#f5f4ed')
        fig.patch.set_facecolor('#f5f4ed')

        plt.bar(categories,values, color = c, width = 0.4)
        addlabels(categories, values)
        plt.title("Your Total Spending by Category")
        plt.xlabel('Categories')
        plt.ylabel('$')
        plt.savefig(img, format = "png")
        plot_url = base64.b64encode(img.getvalue()).decode('utf8')
        plt.close()

        img2 = BytesIO()
        fig = plt.figure(figsize = (8, 5))
        ax = plt.axes()
        ax.set_facecolor('#f5f4ed')
        fig.patch.set_facecolor('#f5f4ed')
        plt.pie(values, labels = categories, colors = c, labeldistance=1.15, wedgeprops = { 'linewidth' : 1, 'edgecolor' : 'white' }, autopct = '%.2f%%')
        plt.title("Your Total Spending by Category")
        plt.savefig(img2, format = "png")
        plot_url2 = base64.b64encode(img2.getvalue()).decode('utf8')
        plt.close()
        

    return render_template('spending.html', plot_url=plot_url, plot_url2 = plot_url2)