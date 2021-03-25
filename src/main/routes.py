from flask import render_template, Blueprint, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user

from src.models import Link
from src.extensions import db
from src.main.forms import UrlCreated, UrlCreate, UrlSubmit  # UrlSubmit


main = Blueprint('main', __name__, template_folder='templates')


@main.route('/<url_short>')
def redirect_url(url_short):
    link = Link.query.filter_by(url_short=url_short).first_or_404()
    link.clicks = link.clicks + 1
    db.session.commit()
    # return redirect(link.url_org)
    return render_template('link_redirect.html', redirect_path=link.url_org)


# @main.route("/home")
@main.route('/dashboard')
def stats():
    links = Link.query.all()
    return render_template('link_stats.html', title='Dashboard', links=links)


@main.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404
    # abort(400, description='Invalid URL scheme provided')


@main.route("/", methods=['GET', 'POST'])
def link_create():
    form = UrlSubmit()
    return render_template('link_submit.html', title='shorten', form=form, legend='New Link')


@main.route('/link', methods=['POST'])
def single_link():
    form = UrlCreated()
    url_org = request.form['url_org']

    if url_org[:7] != 'http://' and url_org[:8] != 'https://':
        flash('Invalid URL scheme provided', 'danger')
        return redirect(url_for('main.link_create'))
    # if total >= 238.328:
    #     flash('Maximum links reached', 'danger')
    link = Link(url_org=url_org, url=current_user)
    db.session.add(link)
    db.session.commit()
    flash('Link successfully shortened ', 'success')
    form.url_org.data = url_org
    form.url_short.data = url_for('main.link_create', _external=True) + link.url_short
    # form.url_short.data = link.url_short
    return render_template('link_create.html', title='new link created',
                           url_short=link.url_short, url_org=url_org, form=form, legend='Short Link')


@main.route("/link/<int:id>")
def edit_link(id):
    link = Link.query.get_or_404(id)
    return render_template('link_single.html', url_org=link.url_org, link=link)


# create url redirect to home
# deprecated
@main.route("/link/new", methods=['GET', 'POST'])
@login_required
def new_link():
    form = UrlCreate()
    if form.validate_on_submit():
        link = Link(url_org=form.url_org.data, url=current_user)
        db.session.add(link)
        db.session.commit()
        flash('Link created', 'success')
        return redirect(url_for('main.stats'))
    return render_template('link_create_1.html', title='New link', form=form, legend='New Link')

