from bs4 import BeautifulSoup
import requests
import os
from MySQLdb import connect


def connect_db(**kargs):
	if len(kargs) < 3:
		raise ValueError("expected at least 3 argument")
	try:
		conn = connect(**kargs)
	except:
		return "failed to connect check connection paramaters"
	else:
		cursor = conn.cursor()
	return conn,cursor

def execute_sql(cur,cmd):
	cur.execute(cmd)

def select_item(bs,css_selector):
	if bs:
		return bs.select(css_selector)

def fetch_data(url):
	try:
		req = requests.get(url)
	except:
		return "An error has occured while connecting to {}".format(url)
	else:
		return BeautifulSoup(req.text,"lxml")

def transform_price(price):
	import re
	price =[value.strip() for value in re.split("[-–]",price) ]
	if len(price)==1:
		return [price[0],price[0]]
	return price

def process_item(item,transform_name=None,transform_price=None):
	import re
	pattern = re.compile("(N[0-9,]+.*[N]*[0-9,]*)")
	price = transform_price( pattern.search(item).group(0) ) if transform_price else pattern.search(item).group(0)
	name  = pattern.sub("",item)
	return name.replace("–",""),price 

def main():
	USERNAME = os.getenv("USERNAME")
	DATABASE = os.getenv("DATABASE")
	PASSWORD = os.getenv("PASSWORD")
	HOST     = os.getenv("HOST")

	url = "https://nigerianprice.com/prices-of-foodstuff-in-nigeria"
	bs  = fetch_data(url)
	items = {}
	offset  = 3
	end_offset = 10
	for ul in select_item(bs,"ul")[offset:end_offset]:
		for price in ul.children:
			key,value = process_item(price.string,transform_price=transform_price)
			items[key] = value

	conn,cur = connect_db(user=USERNAME,passwd=PASSWORD,host=HOST,db=DATABASE)
	SQL_STATEMENT = """
			create table if not exists prices(id int(4) not null auto_increment,
				type varchar(100),from_price varchar(100),
				to_price varchar(100),primary key(id)
			)
			"""

	execute_sql(cur,SQL_STATEMENT)
	for key in items:
		cmd = "insert into prices(type,from_price,to_price) values(%s,%s,%s)"
		args = [key]+items[key]
		print(args)
		cur.execute(cmd,args)
	conn.commit()
	cur.execute("select * from prices")
	cur.close()
	conn.close()

if __name__=="__main__":
	main()
