from scrapy import Spider

class BccCrawler(Spider):
	name = "bbcCrawler"
	start_urls = ["https://bbc.com/"]
	allowed_domains = ["bbc.com"]

	def parse(self,response):
		title = response.css("h1[id^=page-title]::text").get()
		yield {"title of the site":title}
		print(title)

		for news in response.xpath("//li[contains(@class,'media-list__item')]"):
			data={
				"title":news.css("h3.media__title a.media__link::text ").get(),
				"category":news.css("a.media__tag::text").get()

				}
			if all(data.values()):
				print(data)
