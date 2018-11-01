# -*- coding: utf-8 -*-
"""两种下载方式的对比"""
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from twisted.enterprise import adbapi
from pymysql import cursors  # 游标类


class JianshuSpiderPipeline(object):
    """正常下载，一个线程累到死"""

    def __init__(self):
        # 设置数据库的连接方式
        dbparams = {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "password": "yang123",
            "database": "yangyi",
            "charset": "utf8",
        }
        # 建立连接
        self.conn = pymysql.connect(**dbparams)
        # 获取游标
        self.cursor = self.conn.cursor()
        # 初始化sql语句
        self._sql = None

    def process_item(self, item, spider):
        # 获取传递的数据，使用sql语句，传递一次写入一次(没有效率提升)
        self.cursor.execute(self.sql, (item["title"], item["content"],
                                       item["author"], item["avatar"], item["pub_time"], item["article_id"],
                                       item["origin_url"]))
        # 写入一次提交一次
        self.conn.commit()
        return item

    @property
    def sql(self):
        # 待执行的sql语句
        if not self._sql:
            self._sql = """
            insert into jianshu(id, title, content, author,
            avatar, pub_time, article_id, origin_url)
            values(null,%s,%s,%s,%s,%s,%s,%s)
            """
            return self._sql
        return self._sql


class JianshuTwistedPipeline(object):
    """MySQL连接池操作，多个线程同时操作(异步下载)"""

    def __init__(self):
        # 获取数据库的连接方式，并指定指定要执行的cursors类
        dbparams = {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "password": "yang123",
            "database": "yangyi",
            "charset": "utf8",
            "cursorclass": cursors.DictCursor,
        }
        # 用指定的pymysql连接数据库生成连接池。adbapi提供了异步访问数据库的机制
        self.dbpool = adbapi.ConnectionPool("pymysql", **dbparams)
        # 初始化sql语句
        self._sql = None

    @property
    def sql(self):
        # 设置待执行的sql语句
        if not self._sql:
            self._sql = """
                insert into jianshu(id, title, content, author,
                avatar, pub_time, article_id, origin_url, read_count, like_count, word_count,
                subjects, comment_count)
                values(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """
            return self._sql
        return self._sql

    def process_item(self, item, spider):
        # 以异步方式调用insert_item函数,传入一个Transaction对象和item，并执行sql语句后会自动commit(效率提升)
        defer = self.dbpool.runInteraction(self.insert_item, item)
        # 回调错误信息并在函数handle_error中打印
        defer.addErrback(self.handle_error, item, spider)

    def insert_item(self, cursor, item):
        # 写入数据
        cursor.execute(self.sql, (item["title"], item["content"],
                                  item["author"], item["avatar"], item["pub_time"], item["article_id"],
                                  item["origin_url"], item["read_count"], item["like_count"], item["word_count"],
                                  item["subjects"], item["comment_count"]))

    def handle_error(self, error, item, spider):
        # 打印错误信息
        print("*" * 10 + "error" + "*" * 10)
        print(error)
        print("*" * 10 + "error" + "*" * 10)
