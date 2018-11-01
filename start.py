"""设置爬虫运行的简单方式"""
from scrapy import cmdline

cmdline.execute("scrapy crawl js".split())