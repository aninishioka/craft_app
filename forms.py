from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, SelectField, FieldList, FormField, Form, SubmitField, DateField
from wtforms.validators import InputRequired, Length, Email, Optional, URL, NumberRange


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


class EditUserForm(FlaskForm):
    """Form to edit user."""

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


class YarnForm(Form):
    """Form to add yarn to project."""

    yarn_name = StringField(
        "Yarn Name",
        validators=[Optional(), Length(max=100)]
    )

    color = StringField(
        "Color",
        validators=[Optional(), Length(max=100)]
    )

    dye_lot = StringField(
        "Dye lot",
        validators=[Optional(), Length(max=20)]
    )

    weight = SelectField(
        "Weight",
        choices=[
            ('lace', 'Lace'),
            ('super_fine', 'Super Fine'),
            ('fine', 'Fine'),
            ('light', 'Light'),
            ('medium', 'Medium'),
            ('bulky', 'Bulky'),
            ('super_bulky', 'Super Bulky'),
            ('jumbo', 'Jumbo')
        ],
        validators=[Optional()]
    )

    skein_weight = IntegerField(
        "Skein weight",
        validators=[Optional(), NumberRange(min=0)]
    )

    skein_weight_unit = SelectField(
        "Skein weight unit",
        choices=[('grams', 'grams'), ('ounces', 'ounces')]
    )

    skein_length = IntegerField(
        "Skein length",
        validators=[Optional(), NumberRange(min=0)]
    )

    skein_length_unit = SelectField(
        "Skein length unit",
        choices=[('yards', 'yards'), ('meters', 'meters')]
    )

    num_skeins = IntegerField(
        "Number of Skeins",
        validators=[Optional(), NumberRange(min=0)]
    )

    delete = SubmitField(
        "Remove"
    )


class NeedleForm(Form):
    """Form to add needles to project."""

    size = SelectField(
        'Needle size',
        # TODO: assign choices dynamically from db
        choices=[
            ('US 00000000 - 0.5 mm', 'US 00000000 - 0.5 mm'),
            ('US 000000 - 0.75 mm', 'US 000000 - 0.75 mm'),
            ('US 00000 - 1.0 mm', 'US 00000 - 1.0 mm'),
            ('US 0000 - 1.25 mm', 'US 0000 - 1.25 mm'),
            ('US 000 - 1.5 mm', 'US 000 - 1.5 mm'),
            ('US 00 - 1.75 mm', 'US 00 - 1.75 mm'),
            ('US 0 - 2.0 mm', 'US 0 - 2.0 mm'),
            ('US 1 - 2.25 mm', 'US 1 - 2.25 mm'),
            ('US 1.5 - 2.5 mm', 'US 1.5 - 2.5 mm'),
            ('US 2 - 2.75 mm', 'US 2 - 2.75 mm'),
            ('US 2.5 - 3.0 mm', 'US 2.5 - 3.0 mm'),
            ('US 3 - 3.25 mm', 'US 3 - 3.25 mm'),
            ('US 4 - 3.5 mm', 'US 4 - 3.5 mm'),
            ('US 5 - 3.75 mm', 'US 5 - 3.75 mm'),
            ('US 6 - 4.0 mm', 'US 6 - 4.0 mm'),
            ('4.25 mm', '4.25 mm'),
            ('US 7 - 4.5 mm', 'US 7 - 4.5 mm'),
            ('4.75 mm', '4.75 mm'),
            ('US 8 - 5.0 mm', 'US 8 - 5.0 mm'),
            ('US 9 - 5.5 mm', 'US 9 - 5.5 mm'),
            ('US 10 - 6.0 mm', 'US 10 - 6.0 mm'),
            ('US 10.5 - 6.5 mm', 'US 10.5 - 6.5 mm'),
            ('7.0 mm', '7.0 mm'),
            ('7.5 mm', '7.5 mm'),
            ('US 11 - 8.0 mm', 'US 11 - 8.0 mm'),
            ('US 13 - 9.0 mm', 'US 13 - 9.0 mm'),
            ('US 15 - 10.0 mm', 'US 15 - 10.0 mm'),
            ('US 17 - 12.0 mm', 'US 17 - 12.0 mm'),
            ('US 19 - 15.0 mm', 'US 19 - 15.0 mm'),
            ('US 35 - 19.0 mm', 'US 35 - 19.0 mm'),
            ('US 50 - 25.0 mm', 'US 50 - 25.0 mm')
        ]
    )

    delete = SubmitField(
        "Remove"
    )


class HookForm(Form):
    """Form to add hooks to project."""

    size = SelectField(
        'Hook size',
        # TODO: assign choices dynamically from db
        choices=[
            ('0.6 mm', '0.6 mm'),
            ('0.7 mm', '0.7 mm'),
            ('0.75 mm', '0.75 mm'),
            ('0.85 mm', '0.85 mm'),
            ('0.9 mm', '0.9 mm'),
            ('1.0 mm', '1.0 mm'),
            ('1.05 mm', '1.05 mm'),
            ('1.1 mm', '1.1 mm'),
            ('1.15 mm', '1.15 mm'),
            ('1.25 mm', '1.25 mm'),
            ('1.3 mm', '1.3 mm'),
            ('1.4 mm', '1.4 mm'),
            ('1.5 mm', '1.5 mm'),
            ('1.65 mm', '1.65 mm'),
            ('1.75 mm', '1.75 mm'),
            ('1.8 mm', '1.8 mm'),
            ('1.9 mm', '1.9 mm'),
            ('2.0 mm', '2.0 mm'),
            ('2.1 mm', '2.1 mm'),
            ('2.25 mm (B)', '2.25 mm (B)'),
            ('2.35 mm', '2.35 mm'),
            ('2.5 mm', '2.5 mm'),
            ('2.75 mm (C)', '2.75 mm (C)'),
            ('3.0 mm', '3.0 mm'),
            ('3.25 mm (D)', '3.25 mm (D)'),
            ('3.5 mm (E)', '3.5 mm (E)'),
            ('3.75 mm (F)', '3.75 mm (F)'),
            ('4.0 mm (G)', '4.0 mm (G)'),
            ('4.25 mm (G)', '4.25 mm (G)'),
            ('4.5 mm', '4.5 mm'),
            ('5.0 mm (H)', '5.0 mm (H)'),
            ('5.5 mm (I)', '5.5 mm (I)'),
            ('6.0 mm (J)', '6.0 mm (J)'),
            ('6.5 mm (K)', '6.5 mm (K)'),
            ('7.0 mm', '7.0 mm'),
            ('7.5 mm', '7.5 mm'),
            ('8.0 mm (L)', '8.0 mm (L)'),
            ('9.0 mm (M/N)', '9.0 mm (M/N)'),
            ('10.0 mm (N/P)', '10.0 mm (N/P)'),
            ('11.5 mm (P)', '11.5 mm (P)'),
            ('12.0 mm', '12.0 mm'),
            ('15.0 mm (P/Q)', '15.0 mm (P/Q)'),
            ('15.75 mm (Q)', '15.75 mm (Q)'),
            ('19.0 mm (S)', '19.0 mm (S)'),
            ('25.0 mm', '25.0 mm'),
            ('40.0 mm', '40.0 mm')
        ]
    )

    delete = SubmitField(
        "Remove"
    )


class ProgressForm(FlaskForm):
    """Form to change project progress status"""

    progress = SelectField(
        "Status",
        choices=[
            ('Not started', 'Not started'),
            ('In progress', 'In progress'),
            ('Completed', 'Completed'),
            ('Frogged', 'Frogged'),
        ],
        validators=[Optional()]
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

    needles = FieldList(
        FormField(NeedleForm)
    )

    add_needles = SubmitField(
        "Add needles"
    )

    hooks = FieldList(
        FormField(HookForm)
    )

    add_hooks = SubmitField(
        "Add hooks"
    )

    yarns = FieldList(
        FormField(YarnForm)
    )

    add_yarn = SubmitField(
        "Add yarn"
    )

    progress = SelectField(
        "Status",
        choices=[
            ('Not started', 'Not started'),
            ('In progress', 'In progress'),
            ('Completed', 'Completed'),
            ('Frogged', 'Frogged'),
        ],
        validators=[Optional()]
    )


class EditProjectForm(NewProjectForm):
    """Form to edit a project."""


class ProjectTimeLogForm(FlaskForm):
    """Form to log time worked on a project."""

    project = SelectField(
        "Select Project",
        validate_choice=[InputRequired()]
    )

    date = DateField(
        "Date",
        validators=[InputRequired()]
    )

    hours = IntegerField(
        "Hours",
        validators=[Optional(), NumberRange(min=0, max=23)]
    )

    minutes = IntegerField(
        "Minutes",
        validators=[InputRequired(), NumberRange(min=0, max=59)]
    )

    notes = TextAreaField(
        "Notes",
        validators=[Optional()]
    )

class EditTimeLogForm(FlaskForm):
    """Time intervals spent on a project."""

    date = DateField(
        "Date",
        validators=[InputRequired()]
    )

    hours = IntegerField(
        "Hours",
        validators=[Optional(), NumberRange(min=0, max=23)]
    )

    minutes = IntegerField(
        "Minutes",
        validators=[InputRequired(), NumberRange(min=0, max=59)]
    )

    notes = TextAreaField(
        "Notes",
        validators=[Optional()]
    )

class MessageForm(FlaskForm):
    """Compose new message in conversation."""

    message = TextAreaField(
        "Message",
        validators=[InputRequired()]
    )

class SelectUserForm(Form):
    """Select user as participant in conversation"""

    user = SelectField('User')

    delete = SubmitField('Remove')

class NewConversationForm(MessageForm):
    """Create new conversation."""

    # users = FieldList(FormField(SelectUserForm), min_entries=1)
    user = SelectField('User', coerce=int, validators=[InputRequired()])

    add_user = SubmitField("Add User")