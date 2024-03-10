from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()


class User(db.Model):
    """Site user."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    username = db.Column(
        db.String(30),
        nullable=False,
        unique=True
    )

    password = db.Column(
        db.String(150),
        nullable=False
    )


class Note(db.Model):
    """Note written by user."""

    __tablename__ = 'notes'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    title = db.Column(
        db.String(100),
        nullable=False,
        default='New Note'
    )

    designer = db.Column(
        db.String(100),
        nullable=False,
        default=''
    )

    pattern = db.Column(
        db.String(150),
        nullable=False,
        default=''
    )

    gauge = db.Column(
        db.String(150),
        nullable=False,
        default=''
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )


class Yarn(db.Model):
    """Yarn details."""

    __tablename__ = 'yarns'

    brand = db.Column(
        db.String(100),
        nullable=False,
        default=''
    )

    product = db.Column(
        db.String(100),
        nullable=False,
        default=''
    )

    weight = db.Column(
        db.String(30),
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
        db.Integer
    )

    weight_unit = db.Column(
        db.String(10)
    )

    length = db.Column(
        db.Integer
    )

    length_unit = db.Column(
        db.String(10)
    )


class GaugeSwatch(db.Model):
    """Gauge swatches for user notes."""

    ___tablename__ = 'gauge_swatches'

    height = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    width = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    rows = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    column = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )


def connect_db(app):
    """Connect to database."""

    app.app_context().push()
    db.app = app
    db.init_app(app)