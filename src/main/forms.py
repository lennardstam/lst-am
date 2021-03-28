from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL, ValidationError

from src.models import Link


class UrlCreated(FlaskForm):
    url_org = StringField(' Original URL ', validators=[DataRequired(), URL()], render_kw={"placeholder": "Shorten your link."})
    url_short = StringField(' New URL ', render_kw={"placeholder": "..."})


class UrlCreate(FlaskForm):
    url_org = StringField('Shorten', validators=[DataRequired(), URL()], render_kw={"placeholder": "https://..."})
    url_short = StringField('New URL', render_kw={"placeholder": "."})
    submit = SubmitField('Submit')


class LinkUpdate(FlaskForm):
    url_org = StringField('Original Url', validators=[DataRequired(), URL()])
    url_short = StringField('Short Url', validators=[DataRequired()], render_kw={"placeholder": "."})
    submit = SubmitField('Update')

    # def validate_url(self, url_short):
    #     link = Link.query.filter_by(url_short=url_short.data).first()
    #     if link:
    #         raise ValidationError('Link already exists. ')

