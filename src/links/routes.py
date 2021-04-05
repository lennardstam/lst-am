from flask import render_template, Blueprint, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
# from wtforms import ValidationError
import re

# from src.models import Link, Anonymous #User,
from src.extensions import db, login_manager
from src.links.forms import UrlCreate, LinkUpdate  # UrlCreated, UrlSubmit
from src.links.models import Link

main = Blueprint('links', __name__, template_folder='templates')


@main.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404
    # abort(400, description='Invalid URL scheme provided')


@main.route("/", methods=['GET', 'POST'])
def new_link():
    form = UrlCreate()
    if form.validate_on_submit():
        url_org = request.form['url_org']
        url_short = request.form['url_short'] or None
        if current_user.is_anonymous:
            flash('Please login', 'danger')
            return redirect(url_for('users.login'))
        count = Link.query.count()
        if count > 100:
            flash(f'Maximum Links ({count}) reached. Delete links before add new', 'danger')
            return redirect(url_for('links.new_link'))
        pattern = re.compile("\s+")
        if url_short != None and pattern.search(url_short):
            flash('This URL is invalid ', 'danger')
            return render_template('create.html', title='New link', form=form, legend='New Link')
        if Link.query.filter_by(url_short=url_short).first():
            flash('This url already exists ', 'danger')
            return render_template('create.html', title='New link', form=form, legend='New Link')
        link = Link(url_org=url_org, url=current_user, url_short=url_short)
        db.session.add(link)
        db.session.commit()
        flash('Link successfully shortened ', 'success')
        form.url_org.data = url_org
        form.url_short.data = url_for('links.new_link', _external=True) + link.url_short
        # form.url_short.data = link.url_short
        return redirect(url_for('links.edit_link', id=link.id))
    return render_template('links/create.html', title='New link', form=form, legend='New Link')


@main.route('/<url_short>')
def redirect_url(url_short):
    link = Link.query.filter_by(url_short=url_short).first_or_404()
    link.clicks = link.clicks + 1
    db.session.commit()
    # return redirect(link.url_org)
    return render_template('links/redirect.html', redirect_path=link.url_org)


@main.route('/link/list/<int:id>', methods=['GET', 'POST'])
@login_required
# def dashboard_single(id):
def list_links(id):
    # if current_user.id != 1:
    #     abort(403)
    if current_user.id == id or current_user.id == 1:
        # links = Link.query.filter(Link.user_id == id).all()
        page = request.args.get('page', 1, type=int)
        links = Link.query.filter(Link.user_id == id).order_by(Link.created.desc()).paginate(page=page, per_page=5)
        # links = Link.query.filter(Link.user_id == id).paginate(page=page, per_page=5)
        link_count = db.session.query(db.func.count()).filter(Link.user_id == id).scalar()
        # flash(f'{link_count}')
    else:
        abort(403)
    return render_template('links/list.html', title='Dashboard', links=links, id=id, link_count=link_count)


@main.route("/link/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_link(id):
    link = Link.query.get_or_404(id)
    form = LinkUpdate()
    if link.url_short == form.url_short.data and link.url_org == form.url_org.data:
        return redirect(url_for('links.edit_link', id=link.id))
    pattern = re.compile("\s+")
    if form.url_short.data != None and pattern.search(form.url_short.data):
        flash('This URL is invalid ', 'danger')
        return redirect(url_for('links.edit_link', id=link.id))
        # return render_template('links.edit_link.html', title='New link', form=form, legend='New Link')
    if link.url_short != form.url_short.data and Link.query.filter_by(url_short=form.url_short.data).first():
        flash('This url already exists ', 'danger')
        return redirect(url_for('links.edit_link', id=link.id))
    # if request.method == 'POST':
    if form.validate_on_submit():
        link.url_short = form.url_short.data
        link.url_org = form.url_org.data
        db.session.commit()
        flash('Link has been updated', 'success')
        return redirect(url_for('links.edit_link', id=link.id))
    elif request.method == 'GET':
        form.url_org.data = link.url_org
        form.url_short.data = link.url_short
    # return render_template("create_post.html", title='Update Post', form=form, legend='Update Post')
    return render_template('links/edit.html', url_org=link.url_org, link=link, form=form, title='Update',legend='Update Link')


@main.route("/link/drop/<int:id>", methods=['POST'])
@login_required
def drop_link(id):
    link = Link.query.get_or_404(id)
    if link.url == current_user or current_user.id == 1:
        db.session.delete(link)
        db.session.commit()
        flash(f'Link #{id} has been deleted', 'success')
        return redirect(url_for('links.dashboard_single', id=current_user.id))
    else:
        abort(403)
