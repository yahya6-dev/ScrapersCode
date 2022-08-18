from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from config import config 
from threading import Timer
from flask_bootstrap import Bootstrap5
import os

db = SQLAlchemy() #set up db instance and
moment = Moment() #moment for proper time rendering
boostrap = Bootstrap5(None)

def run_schedule():
	pass
def create_app(config_name):
	app = Flask(__name__)               #create application factory
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)
	from .main import main
	app.register_blueprint(main)

	boostrap.init_app(app)
	db.init_app(app)
	moment.init_app(app)
	if not app.testing:
		run_schedule()
	return app




