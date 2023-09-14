##sample that fetch 100 non profit from https://www.pledge.to/organizations
##parse them, then store in sqlite
from bs4 import BeautifulSoup
import requests,sqlite3,re
from urllib.request import urlretrieve
import _thread as thread

def connect(url):
	try:
		response = requests.get(url,headers={"user-agent":
                    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0"},timeout=10.0,allow_redirects=True)
	except Exception:
		print("error while trying to fetch to the resource")
		return None
	else:
		return BeautifulSoup(response.text,"html.parser")

def download_image(url):
	name = url.split("/")[-1]
	urlretrieve(url,"outputs/"+name)
	print("image downloaded")
	print(url)

def fetch_100(url):
	bs = connect(url)
	links_url =  []
	if bs:
		page = 2
		while len(links_url) <= 100:
			for img in bs.select("div.h-100.d-flex.flex-column img[src]"):
				thread.start_new_thread(download_image,(img.get("src"),))
			links = bs.find_all("a",{"class":"featured-fundraiser-link"})
			for link in links:
				links_url.append(link.get("href"))
				bg_img = link.parent.select("div.embed-responsive-item.bg-white.bg-cover.featured-fundraiser-image")[0].get("style")
				print(bg_img)
				if bg_img:
					bg_img = bg_img.split(": ")[-1]
					src = bg_img.replace("'"," ").replace("(",'').replace(")",'').replace(";",'').strip()
					src = re.search("\s+https://.*[^\)]",src).group(0).strip()
					thread.start_new_thread(download_image,(src,)) 
			bs = connect(url+"?page=%d"%page)
			page += 1
	return links_url


def open_db(filename):
	conn = sqlite3.connect(filename)
	cursor = conn.cursor()
	cursor.execute("""create table if not exists NonProfit(id integer primary key autoincrement,
	  name varchar(100),
          address varchar(100),
	  causes varchar(100),
          country varchar(100),
	  state varchar(100),
	  gross_income varchar(100),
	  goverment_reg_no varchar(100),
	  description varchar(100),
	  mission varchar(100),
	  website varchar(100),
	  registration_type varchar(100),
	  email varchar(100),
	  phone varchar(100),
	  year_founded varchar(100),
	  date varchar(8),
	  month varchar(12)
        );""")
	return conn,cursor

def write_to_db(filename,results):
	conn,cur = open_db(filename)
	for result in results:
		print("dump")
		cur.execute("insert into NonProfit(name,address,causes,country,state,gross_income,goverment_reg_no,description,mission, website,registration_type,email,phone,year_founded,date,month) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",result)
	conn.commit()


def get_contact(url):
	print(url,"get_contact")
	results = []
	bs = connect(url)
	if not bs: return ['','','']
	text = bs.get_text()
	reg_type = re.search("\d{3}\([a-zA-Z0-9]+\)\d",text)
	email = re.search("[a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-z]+",text)
	phone = re.search("\(\d{3}\)\s*\d{3}-\d{4}",text) 
	return [reg_type.group(0) if reg_type else '',
	 email.group(0) if email else '',
       	 phone.group(0) if phone else '' ]

def get_date_month(string):
	date = re.search("\s+(\d{2}),\s+\d{4}",string)
	month = re.search("\s+([a-zA-Z]+)\s+\d{2},\s+\d{4}",string)
	return date.group(1) if date else '',month.group(1) if month else ''

def parse_nonprofit(bs,reg):
	name = bs.find("h1",{"class":"h3"})
	address_rest = bs.find("span",{"class":"p-street-address"}).next_siblings if bs.find("span",{"class":"p-street-address"}) else ''
	address_rest = [l.get_text() for l in bs.find("span",{"class":"p-street-address"}).next_siblings] if address_rest else []
	address_head = bs.find("span",{"class":"p-street-address"}).get_text() if address_rest else ''
	address = address_head + ''.join(address_rest)
	causes = ",".join([tag.get_text() for tag in bs.select(" ul.list-inline.text-center a")[:-1]])  if bs.select("ul.list-inline.text-center a") else ''
	country = bs.select("ul.list-inline.text-center a")[-1].get_text()
	state = bs.find("abbr",{"class":"p-region"}).get("title")  if bs.find("abbr",{"class":"p-region"}) else '' #title
	website = bs.select("li.px-1.px-sm-2 a")[0].get("href") if bs.select("li.px-1.px-sm-2 a") else ''  	   #href
	mission = "".join([text.get_text() for text in bs.select("section.mb-5 p")])
	description = bs.select("section.mb-5 div")[0].get_text()
	gross_income =  bs.select("p.mt-3.mb-0.text-muted.text-nowrap")
	gross_income = gross_income[0].find("b").get_text() if gross_income else ''
	goverment_reg_no = reg
	year_founded = re.search("[^$]\d{4}",mission).group(0) if re.search("[^$]\d{4}",mission) else ''
	reg_type,email,phone = get_contact(website)
	date,month = get_date_month(mission)

	return [name.get_text() if name else '',
		  address,causes,country,state,gross_income,
		  goverment_reg_no,description,mission,website,
		  reg_type,email,phone,year_founded,date,month]

if __name__=="__main__":
	results = [] ##all of the parsed data are here
	links_100 = fetch_100('https://www.pledge.to/organizations')
	for link in links_100:
		print(link)
		url =  "https://www.pledge.to"+link
		reg = url.split("/")[-2]
		bs  = connect(url)
		result = parse_nonprofit(bs,reg)
		if result:
			results.append(result)
			print(result)
	write_to_db("test1.sql",results)
	print("done ")
