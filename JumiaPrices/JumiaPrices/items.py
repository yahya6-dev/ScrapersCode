# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JumiapricesItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class MyItem(scrapy.Item):
	title = scrapy.Field()
	price = scrapy.Field()
	original_price = scrapy.Field()



