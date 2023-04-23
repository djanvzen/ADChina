import scrapy
from ..items import AdChinaSpiderItem


class AdChinaNbsSpiderSpider(scrapy.Spider):
    name = "ad_china_nbs_spider"
    allowed_domains = ["stats.gov.cn"]
    start_urls = ["http://www.stats.gov.cn/sj/tjbz/tjyqhdmhcxhfdm/2022/index.html"]

    def parse(self, response):
        # 解析省级
        province_list = response.xpath('//tr[@class="provincetr"]/td/a')
        for province in province_list:
            item = AdChinaSpiderItem()
            item['name'] = province.xpath('text()').extract_first()
            item['code'] = province.xpath('@href').re_first(r'(\d{2}).html')
            item['parent_code'] = ''
            if item['code']:
                item['code'] = item['code'] + '0000000000'
                url = response.urljoin(province.xpath('@href').extract_first())
                yield scrapy.Request(url, callback=self.parse_city, meta={'province': item})

    # def parse_city(self, response):
    #     # 解析地市
    #     province = response.meta['province']
    #     for city in response.xpath('//tr[@class="citytr"]'):
    #         item = AdChinaSpiderItem()
    #         item['name'] = city.xpath('./td[2]/a/text()').extract_first()
    #         item['code'] = city.xpath('./td[1]/a/text()').extract_first()
    #         item['parent_code'] = province.get('code')
    #         if item['code']:
    #             url = response.urljoin(city.xpath('./td[2]/a/@href').extract_first())
    #             yield scrapy.Request(url, callback=self.parse_county, meta={'province': province, 'city': item})
    #
    # def parse_county(self, response):
    #     # 解析区县
    #     province = response.meta['province']
    #     city = response.meta['city']
    #     for county in response.xpath('//tr[@class="countytr"]'):
    #         item = AdChinaSpiderItem()
    #         item['parent_code'] = city.get('code')
    #         item['name'] = county.xpath('./td[2]/a/text()').extract_first()
    #         item['code'] = county.xpath('./td[1]/a/text()').extract_first()
    #
    #         if item['code']:
    #             url = response.urljoin(county.xpath('./td[2]/a/@href').extract_first())
    #             yield scrapy.Request(url,
    #                                  callback=self.parse_town,
    #                                  meta={'province': province, 'city': city, 'county': item})
    #         elif item['name'] == '市辖区':
    #             yield item
    #
    # def parse_town(self, response):
    #     # 解析下一级页面
    #     province = response.meta['province']
    #     city = response.meta['city']
    #     county = response.meta['county']
    #     for town in response.xpath('//tr[@class="towntr"]'):
    #         item = AdChinaSpiderItem()
    #         item['parent_code'] = county.get('code')
    #         item['name'] = town.xpath('./td[2]/a/text()').extract_first()
    #         item['code'] = town.xpath('./td[1]/a/text()').extract_first()
    #
    #         if item['code']:
    #             url = response.urljoin(town.xpath('./td[2]/a/@href').extract_first())
    #             yield scrapy.Request(url,
    #                                  callback=self.parse_village,
    #                                  meta={'province': province, 'city': city, 'county': county, 'town': item})
    #         else:
    #             yield item
    #
    # def parse_village(self, response):
    #     # 解析下一级页面
    #     province = response.meta['province']
    #     city = response.meta['city']
    #     county = response.meta['county']
    #     town = response.meta['town']
    #     for village in response.xpath('//tr[@class="villagetr"]'):
    #         item = AdChinaSpiderItem()
    #         item['parent_code'] = town.get('code')
    #         item['name'] = village.xpath('./td[3]/a/text()').extract_first()
    #         item['code'] = village.xpath('./td[1]/a/text()').extract_first()
    #
    #         meta={'province': province, 'city': city, 'county': county, 'town': town, 'village': item}
    #         yield item