from . import db

class Prices(db.Model):
	__tablename__="prices"
	id = db.Column(db.Integer,primary_key=True)
	phone = db.Column(db.String(200),unique=True,index=True)
	price = db.Column(db.String(200),index=True)


