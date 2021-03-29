from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL, Optional, length, Regexp, ValidationError

from src.models import Link


class UrlCreate(FlaskForm):
    url_org = StringField('Shorten', validators=[DataRequired(), URL()], render_kw={"placeholder": "https://..."})
    # url_short = StringField('New URL', validators=[Optional(strip_whitespace=True), length(max=10)], render_kw={"placeholder": "...."})
    url_short = StringField('New URL', validators=[Optional(strip_whitespace=True), length(max=10), Regexp(r'^[\w.@+-]+$')], render_kw={"placeholder": "...."})
    # url_short = StringField('New URL', validators=[Regexp(r'^[\w.@+-]+$'), Optional(strip_whitespace=True), length(max=10)], render_kw={"placeholder": "...."})
    submit = SubmitField('Submit')


class LinkUpdate(FlaskForm):
    url_org = StringField('Original Url', validators=[DataRequired(), URL()])
    url_short = StringField('New URL', validators=[DataRequired(), Optional(strip_whitespace=True), length(max=10), Regexp(r'^[\w.@+-]+$')], render_kw={"placeholder": "...."})
    # url_short = StringField('New URL', validators=[DataRequired(),Optional(strip_whitespace=True), length(max=10), Regexp(r'^[\w.@+-]+$')], render_kw={"placeholder": "."})
    submit = SubmitField('Update')

    # def validate_url(self, url_short):
    #     link = Link.query.filter_by(url_short=url_short.data).first()
    #     if link:
    #         raise ValidationError('Link already exists. ')

