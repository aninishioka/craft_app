from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Length, Email, Optional, URL


class CSRFProtectForm(FlaskForm):
    """For routes that need CSRF protection."""

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
        'Password',
        validators=[InputRequired(), Length(min=6, max=50)]
    )


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField(
        'Username',
        validators=[InputRequired()]
    )

    password = PasswordField(
        'Password',
        validators=[InputRequired()]
    )


class NewProjectForm(FlaskForm):
    """Form to add new project."""

    title = StringField(
        "Title",
        validators=[Optional(), Length(max=100)],
    )

    pattern = StringField(
        "Pattern Name",
        validators=[Optional(), Length(max=100)]
    )

    designer = StringField(
        "Pattern designer",
        validators=[Optional(), Length(max=100)]
    )

    needles = StringField(
        "Needles",
        validators=[Optional(), Length(max=50)]
    )

    content = TextAreaField(
        "Notes",
        validators=[Optional()]
    )
