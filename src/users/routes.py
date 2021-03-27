from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_user, current_user, logout_user, login_required
from src import db, bcrypt
from src.users.forms import RegistrationForm, LoginForm, UpdateAccountForm
from src.models import User

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
# @login_required
def register():
    # if current_user.is_authenticated:
    #     return redirect(url_for('main.link_create'))
    form = RegistrationForm()
    if current_user.username == "demo" and request.method == 'POST':
        flash('This demo account cant register users.', 'warning')
        return redirect(url_for('users.register'))
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account has been created for {form.username.data}', 'success')
        return redirect(url_for('users.login'))
    return render_template('user_register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.new_link'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.new_link'))
        else:
            flash('Login failed', 'danger')
    return render_template('user_login.html', title='login', form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.new_link'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if current_user.username == "demo" and request.method == 'POST':
        flash('This demo account is static.', 'warning')
        return redirect(url_for('users.account'))
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('account updated', 'succes')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('user_account.html', title='Account', form=form)

