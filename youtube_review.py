from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from urllib.request import urlretrieve
import argparse


MAX_DELAY = 30
def setup_driver(url):
	options = Options()		#set preferences and return a new driver
	#options.headless=True
	driver = Firefox(options=options)
	driver.get(url)
	driver.implicitly_wait(MAX_DELAY)
	return driver


def get_comments(driver): 				#for the comment to display 
	try:
		comments = WebDriverWait(driver,MAX_DELAY).until(
			EC.presence_of_element_located((By.ID,"body"))
			)
	except:
		print("Make sure copy the full video url or the page is loading slowly")  #may be the connection is too slow,invalid video url
		get_comments(driver)
	else:
		comments = driver.find_elements(By.ID,"body")
		return comments

def total_comments(driver):
		try:
			count =  WebDriverWait(driver,MAX_DELAY).until(EC.presence_of_element_located((By.XPATH,
					"//yt-formatted-string[@class='count-text style-scope ytd-comments-header-renderer']/span[@class='style-scope yt-formatted-string']")))
		except:
			print("connection too slow")
			return total_comments(driver)
		return count.text

def parse_comment(comment):
	author_img = comment.find_element(By.ID,"img").get_attribute("src")      #extract the author img and commment like number reply		
	author_name = comment.find_element(By.ID,"author-text").text
	created = comment.find_element(By.TAG_NAME,"yt-formatted-string").text
	author_text = comment.find_element(By.ID,"content-text").text
	vote_count = comment.find_element(By.XPATH,"//span[@id='vote-count-left']").get_attribute("aria-label")

	return author_img,author_name,created,author_text,vote_count

def save_result(img,name,created,text,like):         #save the scraped result to local filesystem
	import os,string
	basedir = os.path.abspath(os.path.dirname(__file__))
	try:
		norm_name = name.strip(string.whitespace+' ')
		path = os.path.join(basedir, "results/"+norm_name)
		os.makedirs(path)
	except:
		print("not saved or file exists")
	else:
		open(path+"/result","w").write("%s %s %s %s"%(name,created,text,like))
		try:
			urlretrieve(img,path+"/photo.png")
		except:
			pass
	print("saved")

if __name__=="__main__":
	parser = argparse.ArgumentParser(description="Youtube video commments")
	parser.add_argument("url",help="url of the video")
	args = parser.parse_args()
	url  = args.url
	driver = setup_driver(url)
	count = 0
	comments = []
	step = 300
	size = 0
	WAIT_FOR_IMG = 10
	BODY_SCROLL = 400
	while True:
		driver.execute_script("window.scrollTo(0,%d)"%step)
		count = total_comments(driver)
		comments= get_comments(driver)
		comments[-1].click()
		step += BODY_SCROLL
		driver.implicitly_wait(WAIT_FOR_IMG)
		print(len(comments))
		if len(comments) == int(count):
			break
		comments =  comments[size:]
		for comment in comments:
			#print(parse_comment(comment))
			image,name,created,text,like = parse_comment(comment)
			save_result(image,name,created,text,like)
		size = len(comments)
	driver.close()
