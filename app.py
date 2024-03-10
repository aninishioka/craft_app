from flask import Flask
from models import connect_db


app = Flask(__name__)


connect_db()