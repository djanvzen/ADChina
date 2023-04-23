# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AdChinaSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 定义要抓取的数据结构
    parent_code = scrapy.Field()
    code = scrapy.Field()
    name = scrapy.Field()
