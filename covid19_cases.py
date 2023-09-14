import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_remote(url):
	try:
		response = requests.get(url,headers={"User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0"})	#fetch the remote resource
	except:										#terminate on an error
		print("Check your connection")
		exit(-1)
	return BeautifulSoup(response.text,"lxml")

def parse(bs):
	headers = [child.get_text() for child in bs.select("table thead th")] #parse content
	outputs = [[] for i in range (len(headers))]
	#print(headers,outputs)
	for tr in bs.select("table tr")[1:]:
		step = 0
		for td in tr.find_all("td"):
			print(td.get_text())
			outputs[step].append(td.get_text().strip())
			step += 1
			print()
	data = {}
	for i in range(len(headers)):
		data[headers[i]] = outputs[i]				#write them as {key:value} key = column while value= 
	return data							#corresponding values of a column

def write_excel(data):
	df = pd.DataFrame(data=data)
	df.to_excel("covid_cases.xls")
	print("finished saved to => covid_cases.xls")

if __name__=="__main__":
	bs = fetch_remote("https://covid19.ncdc.gov.ng")
	output = parse(bs)
	print(output)
	write_excel(output)
