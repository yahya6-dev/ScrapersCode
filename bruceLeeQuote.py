from bs4 import BeautifulSoup
import requests
import re

URL = "https://en.wikiquote.org/wiki/Bruce_Lee"

def fetch_quote(url):
	try:
		response = requests.get(url)
	except:
		print("Failed to connect to %s"%url)
		exit(-1)
	return BeautifulSoup(response.text,"lxml")



def bs_select(bs,selector):
	if bs: return bs.select(selector)


def parse_quote(quote):
	res   = quote.contents
	odd_tags = []
	for i  in range(len(res)):
		tag = res[i]
		if "<" in tag:
			odd_tags.append([i,BeautifulSoup(tag,'lxml').string])
			res.remove(tag)

	for index,tag in odd_tags:
		res.insert(index,tag)
	return {"quote":" ".join([tag.string for tag in res] )}




def main(url):
	bs = fetch_quote(url)
	offset = 11

	for quote in bs_select(bs,"ul li b")[:-offset]:
		if quote.string:
			print({"quote":quote.string})
			print()
		else:
			try:
				print(parse_quote(quote))
				print()
			except Exception as e:
				print(re.sub("<[a-zA-Z/]*>+","",str(quote)))

if __name__=="__main__":
	main(URL)
