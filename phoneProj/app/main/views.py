from . import main
from flask import render_template
from ..models import Prices
from datetime import datetime
from flask import request

def is_mobile(user_agent):
	return "mobile" in user_agent.lower()

@main.route("/")
def index():
	items = Prices.query.all()
	if is_mobile(request.headers.get("User-Agent")):
		return render_template("main1.html",last_update=datetime.utcnow(),phones=items)
	else:
		return render_template("main.html",last_update=datetime.utcnow(),phones=items)
