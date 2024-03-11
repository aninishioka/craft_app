from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, Email, Optional, URL


class SignupForm(FlaskForm):
    """Signup form."""

    username = StringField(
        'Username',
        validators=[InputRequired(), Length(max=30)]
    )

    email = StringField(
        'Email',
        validators=[InputRequired(), Email()]
    )

    image_url = StringField(
        'Image URL',
        validators=[Optional(), Length(max=255), URL()]
    )

    password = PasswordField(
        'password',
        validators=[InputRequired(), Length(min=6, max=50)]
    )


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField(
        'Username',
        validators=[InputRequired()]
    )

    password = PasswordField(
        'password',
        validators=[InputRequired()]
    )


class CSRFProtectForm(FlaskForm):
    """For routes that need CSRF protection."""