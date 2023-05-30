import scrapy


class FincaraizItem(scrapy.Item):
    rooms = scrapy.Field()
    bathrooms = scrapy.Field()
    parking = scrapy.Field()
    area = scrapy.Field()
    stratum = scrapy.Field()
    price = scrapy.Field()
