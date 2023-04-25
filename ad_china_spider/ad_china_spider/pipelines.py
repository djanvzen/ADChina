# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import logging
import copy
import hashlib
from datetime import datetime
from pymysql import cursors
from twisted.enterprise import adbapi


class AdChinaSpiderPipeline:
    def __init__(self, db_pool):
        self.db_pool = db_pool

    @classmethod
    def from_settings(cls, settings):
        db_params = dict(
            host=settings['MYSQL_HOST'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASSWORD'],
            port=settings['MYSQL_PORT'],
            database=settings['MYSQL_DBNAME'],
            use_unicode=True,
            cursorclass=cursors.DictCursor
        )
        db_pool = adbapi.ConnectionPool('pymysql', **db_params)
        return cls(db_pool)

    def process_item(self, item, spider):
        # 只有匹配上关键字的条目才会被保存
        sql_item = {
            "region_code": item["code"],
            "region_name": item["name"],
            "region_level": item["level"],
            "parent_code": item["parent_code"],
            "create_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "create_id": 'ad_china_spider',
        }

        logging.warning(sql_item)
        # 对象拷贝，深拷贝，这里是解决数据重复问题！！！
        async_item = copy.deepcopy(sql_item)

        # 把要执行的sql放入连接池
        insert_info = self.db_pool.runInteraction(self.insert_info, async_item)
        insert_info.addErrback(self.handle_error, sql_item, spider)

        return sql_item

    def insert_info(self, cursor, item):
        sql = "INSERT INTO t_cod_region (region_code, region_name, region_level, parent_code, create_time, create_id) " \
              "VALUES ('{}', '{}', '{}', '{}', '{}', '{}');".format(
            item["region_code"], item["region_name"], item["region_level"], item["parent_code"], item["create_time"], item["create_id"])
        cursor.execute(sql)

    def handle_error(self, failure, item, spider):
        print("failure", failure)
