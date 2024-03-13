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

    projects = db.relationship('Project', backref='user', cascade="all, delete-orphan")


class ProjectNeedle(db.Model):
    """Join table for projects and needles"""

    __tablename__ = 'projects_needles'


    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    project_id = db.Column(
        db.Integer,
        db.ForeignKey('projects.id')
    )

    needle_size = db.Column(
        db.String(25),
        db.ForeignKey('needles.size')
    )


class ProjectHook(db.Model):
    """Join table for projects and needles"""

    __tablename__ = 'projects_hooks'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    project_id = db.Column(
        db.Integer,
        db.ForeignKey('projects.id')
    )

    needle_size = db.Column(
        db.String(25),
        db.ForeignKey('hooks.size')
    )


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
        db.ForeignKey('users.id'),
        nullable=False
    )

    title = db.Column(
        db.String(100),
        nullable=False,
        default='New Project'
    )

    pattern = db.Column(
        db.String(100),
        nullable=False,
        default=''
    )

    designer = db.Column(
        db.String(100),
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

    yarns = db.relationship('Yarn', backref='project', cascade="all, delete-orphan")

    needles = db.relationship(
        'Needle',
        secondary='projects_needles',
        backref='projects'
    )

    projects_needles = db.relationship(
        'ProjectNeedle',
        backref='project',
        cascade="all, delete-orphan"
    )

    hooks = db.relationship(
        'Hook',
        secondary='projects_hooks',
        backref='projects'
    )

    projects_hooks = db.relationship(
        'ProjectHook',
        backref='project',
        cascade="all, delete-orphan"
    )



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
        db.ForeignKey('projects.id')
    )

    yarn_name = db.Column(
        db.String(100),
        nullable=False
    )

    color = db.Column(
        db.String(100),
        nullable=False,
        default=''
    )

    dye_lot = db.Column(
        db.String(20),
        nullable=False,
        default=''
    )

    weight = db.Column(
        db.String(30),
        nullable=False,
        default=''
    )

    skein_weight = db.Column(
        db.Integer
    )

    skein_weight_unit = db.Column(
        db.String(10)
    )

    skein_length = db.Column(
        db.Integer
    )

    skein_length_unit = db.Column(
        db.String(10)
    )

    num_skeins = db.Column(
        db.Integer
    )


class Needle(db.Model):
    """Needle sizes."""

    __tablename__ = 'needles'

    size = db.Column(
        db.String(25),
        primary_key=True
    )


class Hook(db.Model):
    """Hook sizes."""

    __tablename__ = 'hooks'

    size = db.Column(
        db.String(25),
        primary_key=True
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