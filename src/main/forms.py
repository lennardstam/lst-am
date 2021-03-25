from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL, ValidationError

from src.models import Link


# OLD FORM
class UrlSubmit(FlaskForm):
    url_org = StringField('Shorten', validators=[DataRequired(), URL()], render_kw={"placeholder": "Shorten your link."})
    submit = SubmitField('GO')



class UrlCreated(FlaskForm):
    url_org = StringField(' Original URL ', validators=[DataRequired(), URL()])
    url_short = StringField(' New URL ', validators=[DataRequired(), URL()])


class UrlCreate(FlaskForm):
    url_org = StringField('Shorten', validators=[DataRequired(), URL()], render_kw={"placeholder": "Shorten your link."})
    submit = SubmitField('GO')

    def validate_url(self, url_org):
        link = Link.query.filter_by(url_org=url_org.data).first()
        if link:
            raise ValidationError('Email already in use. ')

