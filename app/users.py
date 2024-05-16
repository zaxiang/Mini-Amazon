from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, RadioField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Optional
from .models.user import User
from .models.seller import Seller
from .models.feedback import Feedback
from .models.image import Image
from flask import Blueprint

bp = Blueprint('users', __name__)


class LoginForm(FlaskForm):
    """
    Form for user login with fields for email, password, and remember me option.
    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login. If already authenticated, redirects to the home page. Otherwise, it processes the login form.
    """
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
    """
    Form for new user registration with fields for names, email, and password.
    """
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password')
    password2 = PasswordField('Repeat Password', validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Register')

    # Validate the uniqueness of email
    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handles user registration. If already authenticated, redirects to the home page. Otherwise, it processes the registration form.
    """
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.register(form.email.data,
                         form.password.data,
                         form.firstname.data,
                         form.lastname.data):
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@bp.route('/logout')
def logout():
    """
    Logs out the current user and redirects to the home page.
    """
    logout_user()
    return redirect(url_for('index.index'))


class AccountForm(FlaskForm):
    """
    Form to update existing user account details, including personal information and password.
    """
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat New Password', validators=[EqualTo('password')])
    submit = SubmitField('Update')
    
    def __init__(self, user_id=None, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        self.user_id = user_id
    
    # Validate the uniqueness of email
    def validate_email(self, email):
        if User.email_exists(email.data, update=True, uid=self.user_id):
            raise ValidationError('Already a user with this email.')


@bp.route('/account')
@login_required
def account():
    """
    Displays the current user's account details.
    """
    user = current_user
    return render_template('account.html', title='Account', user=user)


@bp.route('/account_update', methods=['GET', 'POST'])
@login_required
def account_update():
    """
    Allows users to update their account information, handling both GET and POST requests for updating data.
    """
    form = AccountForm(user_id=current_user.id)
    if form.validate_on_submit():
        new_info = {
                'id': current_user.id,
                'firstname': form.firstname.data,
                'lastname': form.lastname.data,
                'email': form.email.data,
                'address': form.address.data,
                'password': form.password.data
        }
        if User.update_information(new_info):
            return redirect(url_for('users.account'))
        else:
            return redirect(url_for('users.account_update'))
        
    # If it's a GET request or form validation fails, display user information
    user = current_user
    return render_template('account_update.html', title='Account Update', form=form, user=user)


class BalanceForm(FlaskForm):
    """
    Form to update user's financial balance, allowing top-ups and withdrawals.
    """
    top_up = RadioField('Top Up', choices=[('10', '$10'), ('50', '$50'), ('100', '$100'), ('200', '$200'), ('500', '$500'), ('1000', '$1000')], validators=[Optional()])
    withdraw = RadioField('Withdraw', choices=[('10', '$10'), ('50', '$50'), ('100', '$100'), ('200', '$200'), ('500', '$500'), ('1000', '$1000'),('all', 'Withdraw All')], validators=[Optional()])
    submit = SubmitField('Update')
    
    def validate_withdraw(self, field):
        if field.data:
            if current_user.is_authenticated:
                user = User.get(current_user.id)  
                if field.data != 'None':
                    withdraw_amount = int(field.data) if field.data != 'all' else user.balance
                    if withdraw_amount > user.balance:
                        raise ValidationError('Insufficient funds to complete this withdrawal.')
            else:
                raise ValidationError('Invalid user.')


@bp.route('/balance', methods=['GET', 'POST'])
@login_required
def balance():
    """
    Manages balance updates for the user, processing both deposits and withdrawals.
    """
    user = User.get(current_user.id)
    form = BalanceForm()
    if form.validate_on_submit():
        top_up_amount, withdraw_amount = 0, 0
        
        if form.top_up.data:
            top_up_amount = int(form.top_up.data)

        if form.withdraw.data == 'all':
            withdraw_amount = user.balance  
        elif form.withdraw.data:
            withdraw_amount = int(form.withdraw.data) if form.withdraw.data else 0
            
        new_balance = user.balance + top_up_amount - withdraw_amount
        print(f'new balance is: {new_balance}')
        
        # Check if the withdraw amount is not more than the current balance
        if new_balance < 0:
            flash('Insufficient balance for this withdrawal.', 'error')
        else:
            if User.update_balance(current_user.id, new_balance):
                return redirect(url_for('users.account'))
    else:
        print("Form errors:", form.errors)
        
    # If it's a GET request or form validation fails, display user information
    return render_template('balance.html', title='Balance', form=form, user=user)


@bp.route('/public-view/<int:uid>')
@login_required
def user_public_view(uid):
    """
    Displays public view of a user's profile, including feedback if the user is a seller.
    """
    user = User.get(uid)
    if not user:
        return redirect(url_for('index.index'))

    feedback_images = {}
    is_seller = Seller.is_seller(uid)
    if is_seller:
        seller = Seller.getByUid(uid)
        feedbacks = Feedback.getBySeller(seller.id)
        if feedbacks:
            # Calculate the average rating
            average_rating = sum(f.rating for f in feedbacks) / len(feedbacks)
            for feedback in feedbacks:
                images = Image.get_feedback_image(feedback.id)
                feedback_images[feedback.id] = images if images else None
        else:
            average_rating = 0  # default value if no feedbacks

        return render_template('user_public_view.html', user=user, feedbacks=feedbacks, user_is_seller=is_seller, average_rating=average_rating, feedback_images=feedback_images)
    
    # If the user is not a seller, just render the template without seller-specific data
    return render_template('user_public_view.html', user=user, user_is_seller=is_seller)