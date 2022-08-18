from scrapy import Spider
from scrapy.mail import MailSender
from JumiaPrices.items import *

class FetchPrices(Spider):
	name = "fetchJumia"
	start_urls = ["https://www.jumia.com.ng/sporting-goods"]


	def parse(self,response):
		output = {"output":[]}
		for item in response.xpath("//article[contains(concat( normalize-space(@class),'' ),'prd')]/a"):
			title = item.css("div.name::text").get() or item.css("h3.name::text").get()
			price = item.css("div.prc::text").get()
			original_price = item.css("div.prc").attrib.get("data-oprc") or item.css("div.old::text").get()

			my_item = MyItem()
			my_item["title"] = title
			my_item["price"] = price
			my_item["original_price"] = original_price

			output["output"].append(my_item)
		yield output

		for link in  response.xpath("//a[@class='pg'][@aria-label]"):
			href = link.attrib.get("href")
			if href:
				yield response.follow(href,callback=self.parse)
