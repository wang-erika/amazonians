from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.user import User
from .models.review import Review
from .models.review import Seller_Review


from flask import Blueprint
bp = Blueprint('users', __name__)


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign in')


@bp.route('/login', methods=['GET', 'POST'])
def login():
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


@bp.route('/balance', methods = ['GET', 'POST'])
def balance():
    form = UpdateBalanceForm()
    if current_user.is_authenticated:
        user = User.get_all(current_user.id)
        #has email, name, password, address, balance
    else:
        return redirect(url_for('users.login'))

    #when form is submitted, call update_balance and redirect to /balance
    if form.validate_on_submit():
        User.update_balance(current_user.id, form.amount.data)
        flash("Added money!")
        return redirect(url_for('users.balance'))
    return render_template('balance.html', user = user, form = form)

class UpdateBalanceForm(FlaskForm):
    amount = FloatField('Amount', validators = [])
    submit = SubmitField('Add')

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
    email = StringField('Email', validators=[Email()])
    address = StringField('Address')
    password = PasswordField('Password')
    password2 = PasswordField(
        'Repeat Password', validators=[EqualTo('password')])
    submit = SubmitField('Update')

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')

@bp.route('/account/edit', methods = ['GET', 'POST'])
def edit_account():
    if current_user.is_authenticated:
        user = User.get_all(current_user.id)
    else:
        redirect(url_for('users.login'))
    form = UpdateForm()
    if form.validate_on_submit():
        '''
        email = form.email.data if len(form.email.data) > 0 else user[0].email
        password = form.password.data if len(form.password.data) > 0 else user[0].password
        firstname = form.firstname.data if len(form.firstname.data) > 0 else user[0].full_name.split(" ")[0]
        lastname = form.lastname.data if len(form.lastname.data) > 0 else user[0].full_name.split(" ")[1]
        '''
        if User.update(current_user.id, email):
            flash('Successfully updated account!')
            return redirect(url_for('users.account_page'))
    return render_template('edit_account.html', user = user, form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))

class SearchBarForm(FlaskForm):
    query = StringField('', validators=[DataRequired()])
    submit = SubmitField('Search')


@bp.route('/view_accounts', methods = ['GET', 'POST'])
def view_accounts():
    if not current_user.is_authenticated:
        redirect(url_for('users.login'))
    form = SearchBarForm()
    account, reviews, seller = None, None, None
    if form.validate_on_submit():
        account = User.get(form.query.data)
        reviews = Review.get_all_product_reviews(form.query.data)
        seller = Seller_Review.get_all_seller_reviews(form.query.data)
    
    else:
        account = User.get(current_user.id)
        reviews = Review.get_all_product_reviews(current_user.id)
        seller = Seller_Review.get_all_seller_reviews(current_user.id)

    return render_template('public_account.html', form = form, account = account, reviews = reviews, seller = seller)