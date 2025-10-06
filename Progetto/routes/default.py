from flask import Blueprint, jsonify, render_template, request
from models.connection import db

from models.model import User


app = Blueprint('default', __name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/index')
def index():
    return render_template('index.html')
