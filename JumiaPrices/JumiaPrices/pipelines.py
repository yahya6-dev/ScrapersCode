# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.mail import MailSender
from MySQLdb import connect

class JumiapricesPipeline:

	def __init__(self,db,user,passwd,host,settings,destination):
		self.db,self.user = db,user
		self.passwd,self.host = passwd,host
		self.mail_dst = destination
		self.settings = settings
		self.mailer   = MailSender.from_settings(settings)


	@classmethod
	def from_crawler(cls,crawler):
		return  cls(crawler.settings.get("DATABASE_NAME"),
			crawler.settings.get("DATABASE_USER"),
			crawler.settings.get("DATABASE_PASS"),
			crawler.settings.get("DATABASE_HOST"),
			crawler.settings.copy(),
			crawler.settings.get("DESTINATION")
			)

	def item_exists(self,filter):
		if self.cur.execute("select * from jumia where title = %s",[filter]):
			return True
		else:
			return False

	def process_item(self, item, spider):

		def item_exists(filter):
                	if self.cur.execute("select * from jumia where title = %s",[filter]):return True
                	else:return False

		CMD = "insert into jumia(title,price,original_price) values(%s,%s,%s)" 
		self.new_items = []

		for output in item["output"]:
				if  not all(output.values()):
					continue

				if not item_exists(output["title"]):
					body="""New item was added its details
						are as follows {} {} {}
						""".format(output["title"],output["price"],output["original_price"])

					self.new_items.append(body)
					title,price,original_price = [v for k,v in output.items()]
					self.cur.execute(CMD,[title,price,original_price])
					print(output["title"])
		self.conn.commit()

	def open_spider(self,spider):
		#connect to the db
		self.conn = connect(user=self.user,
				passwd=self.passwd,db=self.db,
				host=self.host)
		self.cur = self.conn.cursor()

	def close_spider(self,spider):
		#disconnect from the db
		self.conn.close()
		if self.new_items:
			self.mailer.send(to=self.mail_dst,body="\n".join(self.new_items),subject="New Item was added")
