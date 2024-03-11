from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

bcrypt = Bcrypt()
db = SQLAlchemy()

DEFAULT_IMG_URL = (
    "https://icon-library.com/images/default-user-icon/" +
    "default-user-icon-28.jpg")


class User(db.Model):
    """Site user."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    username = db.Column(
        db.String(30),
        nullable=False,
        unique=True
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    image_url= db.Column(
        db.String(255),
        nullable=False,
        default=DEFAULT_IMG_URL
    )

    password = db.Column(
        db.String(150),
        nullable=False
    )

    @classmethod
    def signup(cls, username, email, image_url, password):
        """Creates new user with hashed password and adds to session."""

        hashed = bcrypt.generate_password_hash(password).decode('utf-8')

        user = cls(
            username=username,
            email=email,
            image_url=image_url,
            password=hashed
        )

        db.session.add(user)

        return user

    @classmethod
    def login(cls, username, password):
        """Check user credentials.
        If valid, return user.
        If user not found or credentials invalid, return False
        """

        user = cls.query.filter(User.username == username).one_or_none()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

    projects = db.relationship('Project', backref='user')


class Project(db.Model):
    """Note written by user."""

    __tablename__ = 'projects'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    title = db.Column(
        db.String(100),
        nullable=False,
        default='New Note'
    )

    pattern = db.Column(
        db.String(150),
        nullable=False,
        default=''
    )

    designer = db.Column(
        db.String(100),
        nullable=False,
        default=''
    )

    needles = db.Column(
        db.String(50),
        nullable=False,
        default=''
    )

    content = db.Column(
        db.Text,
        nullable=False,
        default=''
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )

    yarns = db.relationship('Yarn', backref='project')


class Yarn(db.Model):
    """Yarn details."""

    __tablename__ = 'yarns'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    project_id = db.Column(
        db.Integer,
        db.ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False
    )

    # user_id = db.Column(
    #     db.Integer,
    #     db.ForeignKey('user.id', ondelete='CASCADE'),
    #     nullable=False
    # )

    name = db.Column(
        db.String(100),
        nullable=False,
        default=''
    )

    color = db.Column(
        db.String(100),
        nullable=False,
        default=''
    )

    dye_lot = db.Column(
        db.String(100),
        nullable=False,
        default=''
    )

    weight = db.Column(
        db.String(30),
        nullable=False,
        default=''
    )

    amount_weight = db.Column(
        db.Integer
    )

    amount_weight_unit = db.Column(
        db.String(10)
    )

    length = db.Column(
        db.Integer
    )

    length_unit = db.Column(
        db.String(10)
    )


# class Gauge(db.Model):
#     """Gauge details."""

#     ___tablename__ = 'gauges'

#     id = db.Column(
#         db.Integer,
#         primary_key=True,
#         autoincrement=True
#     )

#     note_id = db.Column(
#         db.Integer,
#         db.ForeignKey('note.id', ondelete='CASCADE'),
#         nullable=False
#     )

#     user_id = db.Column(
#         db.Integer,
#         db.ForeignKey('user.id', ondelete='CASCADE'),
#         nullable=False
#     )

#     height = db.Column(
#         db.Integer,
#         nullable=False,
#         default=0
#     )

#     width = db.Column(
#         db.Integer,
#         nullable=False,
#         default=0
#     )

#     unit = db.Column(
#         db.String(10),
#         nullable=False,
#         default='in'
#     )

#     rows = db.Column(
#         db.Integer,
#         nullable=False,
#         default=0
#     )

#     column = db.Column(
#         db.Integer,
#         nullable=False,
#         default=0
#     )


def connect_db(app):
    """Connect to database."""

    app.app_context().push()
    db.app = app
    db.init_app(app)