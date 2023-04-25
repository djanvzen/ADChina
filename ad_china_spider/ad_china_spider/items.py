# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AdChinaSpiderItem(scrapy.Item):
    parent_code = scrapy.Field()
    code = scrapy.Field()
    name = scrapy.Field()
    level = scrapy.Field()
