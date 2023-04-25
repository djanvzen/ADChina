import scrapy
from ..items import AdChinaSpiderItem


class AdChinaNbsSpiderSpider(scrapy.Spider):
    name = "ad_china_nbs_spider"
    allowed_domains = ["stats.gov.cn"]
    start_urls = ["http://www.stats.gov.cn/sj/tjbz/tjyqhdmhcxhfdm/2022/index.html"]

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Cookie': 'wzws_sessionid=gDU4LjIxMC4yMDQuMTA2gjdlZDJkMIFkOWM1NDSgZEZErQ==; SL_G_WPT_TO=zh; SL_GWPT_Show_Hide_tmp=1; SL_wptGlobTipTmp=1; SF_cookie_1=72991020; wzws_cid=5ce79e5f103ef0979af49bd236fdc8f661ead374ef4ba682cb809f0c4d50813b5ddef60f95cfaee3127c8c0ddacb1f78d4c076bb52e566980a5be25aeea17fd98ccc581db6b2e8d550fd2b4a55c33a96',
        'Host': 'www.stats.gov.cn',
        'Proxy-Connection': 'keep-alive',
        'Referer': 'http://www.stats.gov.cn/sj/tjbz/tjyqhdmhcxhfdm/2022/index.html',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
    }
    download_delay = 1

    def parse(self, response):
        # 解析省级
        province_list = response.xpath('//tr[@class="provincetr"]/td/a')
        for province in province_list:
            item = AdChinaSpiderItem()
            item['name'] = province.xpath('text()').extract_first()
            item['code'] = province.xpath('@href').re_first(r'(\d{2}).html')
            item['level'] = 1
            item['parent_code'] = ''
            if item['code']:
                yield item
                item['code'] = item['code'] + '0000000000'
                url = response.urljoin(province.xpath('@href').extract_first())
                yield scrapy.Request(url, callback=self.parse_city, meta={'province': item})

    def parse_city(self, response):
        # 解析地市
        province = response.meta['province']
        for city in response.xpath('//tr[@class="citytr"]'):
            item = AdChinaSpiderItem()
            item['name'] = city.xpath('./td[2]/a/text()').extract_first()
            item['code'] = city.xpath('./td[1]/a/text()').extract_first()
            item['parent_code'] = province.get('code')
            item['level'] = 2

            if item['code']:
                yield item
                url = response.urljoin(city.xpath('./td[2]/a/@href').extract_first())
                yield scrapy.Request(url, callback=self.parse_county, meta={'province': province, 'city': item})

    def parse_county(self, response):
        # 解析区县
        province = response.meta['province']
        city = response.meta['city']
        for county in response.xpath('//tr[@class="countytr"]'):
            item = AdChinaSpiderItem()
            item['parent_code'] = city.get('code')
            item['name'] = county.xpath('./td[2]').xpath('string(.)').extract_first()
            item['code'] = county.xpath('./td[1]').xpath('string(.)').extract_first()
            item['level'] = 3

            yield item
            town_url = county.xpath('./td[2]/a/@href').extract_first()
            if town_url:
                url = response.urljoin(town_url)
                yield scrapy.Request(url,
                                     callback=self.parse_town,
                                     meta={'province': province, 'city': city, 'county': item})


    def parse_town(self, response):
        # 解析乡镇
        province = response.meta['province']
        city = response.meta['city']
        county = response.meta['county']
        for town in response.xpath('//tr[@class="towntr"]'):
            item = AdChinaSpiderItem()
            item['parent_code'] = county.get('code')
            item['name'] = town.xpath('./td[2]').xpath('string(.)').extract_first()
            item['code'] = town.xpath('./td[1]').xpath('string(.)').extract_first()
            item['level'] = 4

            village_url = town.xpath('./td[2]/a/@href').extract_first()

            yield item

            if village_url:
                url = response.urljoin(village_url)
                yield scrapy.Request(url,
                                     callback=self.parse_village,
                                     meta={'province': province, 'city': city, 'county': county, 'town': item})

    def parse_village(self, response):
        # 解析乡村
        province = response.meta['province']
        city = response.meta['city']
        county = response.meta['county']
        town = response.meta['town']
        for village in response.xpath('//tr[@class="villagetr"]'):
            item = AdChinaSpiderItem()
            item['parent_code'] = town.get('code')
            item['name'] = village.xpath('./td[3]').xpath('string(.)').extract_first()
            item['code'] = village.xpath('./td[1]').xpath('string(.)').extract_first()
            item['level'] = 5

            meta = {'province': province, 'city': city, 'county': county, 'town': town, 'village': item}
            yield item