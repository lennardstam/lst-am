from flask import render_template, Blueprint, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
# from wtforms import ValidationError

from src.models import Link, Anonymous #User,
from src.extensions import db, login_manager
from src.main.forms import UrlCreated, UrlCreate, LinkUpdate  # UrlSubmit

main = Blueprint('main', __name__, template_folder='templates')


@main.route('/<url_short>')
def redirect_url(url_short):
    link = Link.query.filter_by(url_short=url_short).first_or_404()
    link.clicks = link.clicks + 1
    db.session.commit()
    # return redirect(link.url_org)
    return render_template('link_redirect.html', redirect_path=link.url_org)


@main.route('/dashboard')
# @login_required
def dashboard():
    links = Link.query.all()
    return render_template('link_stats.html', title='Dashboard', links=links)


@main.route('/stats')
# @login_required
def stats():
    links = Link.query.filter(Link.user_id == current_user.id).all()
    return render_template('link_stats.html', title='Dashboard', links=links)


@main.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404
    # abort(400, description='Invalid URL scheme provided')


@main.route("/", methods=['GET', 'POST'])
def new_link():
    form = UrlCreate()
    return render_template('link_create_1.html', title='New link', form=form, legend='New Link')


@main.route('/link', methods=['POST'])
def single_link():
    form = UrlCreated()
    url_org = request.form['url_org']
    url_short = request.form['url_short'] or None
    # login_manager.anonymous_user = Anonymous

    if url_org[:7] != 'http://' and url_org[:8] != 'https://':
        flash('Invalid URL scheme provided', 'danger')
        return redirect(url_for('main.new_link'))
    count = Link.query.count()
    if count > 1000:
        flash(f'Maximum Links ({count}) reached. Delete links before add new', 'danger')
        return redirect(url_for('main.new_link'))

    # if current_user == current_user:
    #     flash(f'current user: ({current_user})', 'danger')
    # return redirect(url_for('main.new_link'))
    # if current_user.is_anonymous:
    # # # # # if current_user.username == "current_user.is_anonymous":
    #     flash(f'your not logged in ({current_user})', 'danger')
    #     return redirect(url_for('main.new_link'))
    if Link.query.filter_by(url_short=url_short).first():
        flash('This url already exists ', 'danger')
        return redirect(url_for('main.new_link'))
    # if form.validate_on_submit():

    if current_user.is_anonymous:
        quest = Anonymous()
        # user = User.id().where(User.username ** demo).get()
        # quest = Link.url.has(username="demo")
        # url = Link.query.filter_by(url="demo").first()
        # url = Link.user_id.filter_by(username="demo").first()
        # flash(f'current user: ({quest})', 'danger')
        flash('Please login', 'danger')
        return redirect(url_for('users.login'))
        # link = Link(url_org=url_org, url=quest, url_short=url_short)
        # db.session.add(link)
        # db.session.commit()
        # flash('Link successfully shortened ', 'success')
        # form.url_org.data = url_org
        # form.url_short.data = url_for('main.new_link', _external=True) + link.url_short
        # # # # form.url_short.data = link.url_short
        # return render_template('link_create.html', title='new link created', url_short=link.url_short, url_org=url_org, form=form, legend='Short Link')
    link = Link(url_org=url_org, url=current_user, url_short=url_short)
    db.session.add(link)
    db.session.commit()
    flash('Link successfully shortened ', 'success')
    form.url_org.data = url_org
    form.url_short.data = url_for('main.new_link', _external=True) + link.url_short
    # form.url_short.data = link.url_short
    return render_template('link_create.html', title='new link created',
                           url_short=link.url_short, url_org=url_org, form=form, legend='Short Link')


@main.route("/link/<int:id>")
@login_required
def edit_link(id):
    link = Link.query.get_or_404(id)
    return render_template('link_single.html', url_org=link.url_org, link=link)


@main.route("/link/<int:id>/update", methods=['GET', 'POST'])
@login_required
def update_link(id):
    link = Link.query.get_or_404(id)
    if link.url != current_user:
        abort(403)
    form = LinkUpdate()
    if form.validate_on_submit():
        link.url_org = form.url_org.data
        link.url_short = form.url_short.data
        db.session.commit()
        flash('Link has been updated', 'success')
        # return redirect(url_for('update_link', id=link.id))
        return redirect(url_for('main.edit_link', id=link.id))
    elif request.method == 'GET':
        form.url_org.data = link.url_org
        form.url_short.data = link.url_short
    return render_template('link_update.html', title='update link', form=form, legend='Update Link')


