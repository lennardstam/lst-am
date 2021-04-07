from flask import Blueprint, render_template, flash, redirect, url_for, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import func
from flask_mail import Message
import os
from src import db, bcrypt, mail
from src.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm, AdminUpdateAccountForm,
                             RequestResetForm, ResetPasswordForm)
from src.users.models import User
from src.links.models import Link

users = Blueprint('users', __name__, template_folder='templates')


@users.route('/list', methods=['GET'])
@login_required
# def all_users():
def list_users():
    if current_user.id != 1:
        abort(403)
    page = request.args.get('page', 1, type=int)
    link_count = db.session.query(User, Link, func.count(Link.id)).outerjoin(Link, User.id == Link.user_id).group_by(User.id).paginate(page=page, per_page=5)
    user_count = User.query.filter(User.id).count()
    return render_template('users/list.html', title='Users', link_count=link_count, user_count=user_count)


@users.route("/register", methods=['GET', 'POST'])
@login_required
def register():
    form = RegistrationForm()
    if current_user.id != 1:
        abort(403)
    if form.validate_on_submit():
        # hashed_password= User.password_create()
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account has been created for {form.username.data}', 'success')
        return redirect(url_for('users.login'))
    return render_template('users/register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('links.new_link'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('links.new_link'))
        else:
            flash('Login failed', 'danger')
    return render_template('users/login.html', title='login', form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('links.new_link'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    ### DEMO
    if current_user.id == 1 and request.method == 'POST':
        flash('This account is static.', 'warning')
        return redirect(url_for('users.account'))
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('account updated', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        link_total = User.link_count(current_user.id)
    # return render_template('DEL_user_account.html', title='Account', form=form)
        return render_template('users/edit.html', user=current_user, form=form, link_total=link_total)
    return render_template('users/edit.html', user=current_user, title='Account', form=form)


@users.route("/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_user(id):
    form = AdminUpdateAccountForm()
    user = User.query.get_or_404(id)
    link_total = User.link_count(user.id)
    if request.method == 'POST':
        '''Admin user edit lock'''
        # if user.id == 1:
        #     flash('This account is static.', 'warning')
        #     return redirect(url_for('users.edit_user', id=id))
        # if user.username != form.username.data and user.email != form.email.data:
        if form.username.data != user.username:
            check_user = User.query.filter_by(username=form.username.data).first()
            if check_user:
                flash('Username already exists.', 'warning')
                return redirect(url_for('users.edit_user', id=id, user=user, form=form, link_total=link_total))
        if form.email.data != user.email:
            check_email = User.query.filter_by(email=form.email.data).first()
            if check_email:
                flash('Email already in use.', 'warning')
                return redirect(url_for('users.edit_user', id=id, user=user, form=form, link_total=link_total))
        if form.validate_on_submit():
            user.username = form.username.data
            user.email = form.email.data
            db.session.commit()
            flash('account updated', 'success')
            return redirect(url_for('users.edit_user', id=id))
    if request.method == 'GET' and current_user.id == id or current_user.id == 1:
        form.username.data = user.username
        form.email.data = user.email
        # link_total = User.link_count(user.id)
        return render_template('users/edit.html', user=user, form=form, link_total=link_total)
    else:
        abort(403)


@users.route("/drop/<int:id>", methods=['POST'])
@login_required
def drop_user(id):
    if current_user.id != 1:
        abort(403)
    user_acc = User.query.get_or_404(id)
    user_urls = Link.query.filter_by(user_id=id).all()    # if link.url != current_user:
    '''Admin user delete lock'''
    if user_acc.id == 1:
        flash('Admin account cant not be deleted', 'warning')
        return redirect(url_for('users.edit_user', id=id))
    #     abort(403)
    for data in user_urls:
        db.session.delete(data)
    db.session.delete(user_acc)
    db.session.commit()
    flash(f'User {user_acc.username} has been deleted', 'success')
    return redirect(url_for('users.list_users'))


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('links.new_link'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Password reset email is send', 'info')
        return redirect(url_for('users.login'))
    return render_template('users/reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('links.new_link'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('The password has been updated', 'success')
        return redirect(url_for('users.login'))
    return render_template('users/reset_token.html', title='Reset Password', form=form)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='lennardstam@gmail.com', recipients=[user.email])
    msg.body = f'''To reset your password, please visit the following url:
{url_for('users.reset_token', token=token, _external=True)}
'''
    mail.send(msg)