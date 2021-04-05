from flask import Blueprint, render_template, flash, redirect, url_for, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import func

from src import db, bcrypt
from src.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, AdminUpdateAccountForm
from src.users.models import User
from src.links.models import Link

users = Blueprint('users', __name__, template_folder='templates')


@users.route('/list', methods=['GET'])
@login_required
def all_users():
    if current_user.id != 1:
        abort(403)
    page = request.args.get('page', 1, type=int)
    link_count = db.session.query(User, Link, func.count(Link.id)).outerjoin(Link, User.id == Link.user_id).group_by(User.id).paginate(page=page, per_page=5)
    return render_template('user_stats.html', title='Users', link_count=link_count)


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
    return render_template('user_register.html', title='Register', form=form)


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
    return render_template('user_login.html', title='login', form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('links.new_link'))


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
        flash('account updated', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        link_total = User.link_count(current_user.id)
    # return render_template('DEL_user_account.html', title='Account', form=form)
        return render_template('user_single.html', user=current_user, form=form, link_total=link_total)
    return render_template('user_single.html', user=current_user, form=form)


@users.route("/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_user(id):
    form = AdminUpdateAccountForm()
    user = User.query.get_or_404(id)
    link_total = User.link_count(user.id)
    # if form.validate_on_submit() and current_user.id == id or current_user.id == 1:
    # if form.validate_on_submit() and current_user.id == id or current_user.id == 1:
    # if current_user.id == id or current_user.id == 1:
    # if request.method == 'POST' and current_user.id == id or current_user.id == 1:
    if request.method == 'POST':
        # if user.username != form.username.data and user.email != form.email.data:
        if form.username.data != user.username:
            user = User.query.filter_by(username=form.username.data).first()
            if user:
                flash('Username already exists.', 'warning')
                return redirect(url_for('users.edit_user', id=id, user=user, form=form, link_total=link_total))
        if form.email.data != user.email:
            email = User.query.filter_by(email=form.email.data).first()
            if email:
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
        return render_template('user_single.html', user=user, form=form, link_total=link_total)
    else:
        abort(403)


@users.route("/drop/<int:id>", methods=['POST'])
@login_required
def drop_user(id):
    if current_user.id != 1:
        abort(403)
    user_acc = User.query.get_or_404(id)
    user_urls = Link.query.filter_by(user_id=id).all()    # if link.url != current_user:
    #     abort(403)
    for data in user_urls:
        db.session.delete(data)
    db.session.delete(user_acc)
    db.session.commit()
    flash(f'User {user_acc.username} has been deleted', 'success')
    return redirect(url_for('users.all_users'))
