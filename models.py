from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import String
from sqlalchemy.sql.functions import array_agg
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime

bcrypt = Bcrypt()
db = SQLAlchemy()

DEFAULT_IMG_URL = (
    "https://icon-library.com/images/default-user-icon/" +
    "default-user-icon-28.jpg")


class Follow(db.Model):
    """Join table for users and users."""

    __tablename__ = 'follows'

    user_being_followed_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True
    )

    user_following_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True
    )


class Request(db.Model):
    """Join table for users to users.
    Keeps track of requests to follow private accounts."""

    __tablename__ = 'requests'

    user_being_requested_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True
    )

    user_requesting_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True
    )


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

    private = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    projects = db.relationship('Project', backref='user', cascade="all, delete-orphan")

    followers = db.relationship(
        'User',
        secondary="follows",
        primaryjoin=(Follow.user_being_followed_id == id),
        secondaryjoin=(Follow.user_following_id == id),
        backref="following",
    )

    requests_received = db.relationship(
        'User',
        secondary="requests",
        primaryjoin=(Request.user_being_requested_id == id),
        secondaryjoin=(Request.user_requesting_id == id),
        backref="requests_made",
    )

    conversations = db.relationship(
        'Conversation',
        secondary='participants',
        backref='conversations'
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

    def is_following(self, other_user):
        """Checks if user is following other_user."""

        user_list = [user for user in self.following if user == other_user]
        return len(user_list) == 1

    def is_followed_by(self, other_user):
        """Checks if user is followed by other_user."""

        user_list = [user for user in self.followers if user == other_user]
        return len(user_list) == 1

    def get_conversations(self):
        """Gets information about all conversations user a participant in."""

        conversation_ids = [
        c.conversation_id for c
        in Participant.query.filter(Participant.user_id == self.id)]

        return db.session.query(
            Participant.conversation_id,
            array_agg(User.username, type_=ARRAY(String)).label('usernames')
        ).outerjoin(
            Participant
        ).filter(
            Participant.user_id != self.id,
            Participant.conversation_id.in_(conversation_ids)
        ).group_by(
            Participant.conversation_id
        ).all()


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
        db.ForeignKey('projects.id', ondelete="cascade")
    )

    needle_size = db.Column(
        db.String(25),
        db.ForeignKey('needles.size', ondelete="cascade")
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
        db.ForeignKey('projects.id', ondelete="cascade")
    )

    hook_size = db.Column(
        db.String(25),
        db.ForeignKey('hooks.size', ondelete="cascade")
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
        db.ForeignKey('users.id', ondelete='cascade'),
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

    pinned = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    progress = db.Column(
        db.String(100),
        nullable=False,
        default='In progress'
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )

    yarns = db.relationship('Yarn', backref='project')

    needles = db.relationship(
        'Needle',
        secondary='projects_needles',
        backref='projects'
    )

    hooks = db.relationship(
        'Hook',
        secondary='projects_hooks',
        backref='projects'
    )

    time_logs = db.relationship('TimeLog', backref='project')

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
        db.ForeignKey('projects.id', ondelete="cascade")
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

class TimeLog(db.Model):
    """Time intervals spent on a project."""

    __tablename__ = 'time_logs'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    project_id = db.Column(
        db.Integer,
        db.ForeignKey('projects.id', ondelete="cascade")
    )

# TODO: add default
    date = db.Column(
        db.Date,
        nullable=False
    )

    hours = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    minutes = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    notes = db.Column(
        db.Text,
        nullable=False,
        default=''
    )


class Conversation(db.Model):
    """Chat conversation between users."""

    __tablename__ = 'conversations'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )


class Participant(db.Model):
    """Join table for users <--> conversations."""

    __tablename__ = 'participants'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
    )

    conversation_id = db.Column(
        db.Integer,
        db.ForeignKey('conversations.id', ondelete='cascade')
    )


class Message(db.Model):
    """Messages in a conversation."""

    __tablename__ = 'messages'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
    )

    conversation_id = db.Column(
        db.Integer,
        db.ForeignKey('conversations.id', ondelete='cascade')
    )

    text = db.Column(
        db.Text,
        nullable=False,
        default=''
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )

    conversation = db.relationship('Conversation', backref='messages')


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