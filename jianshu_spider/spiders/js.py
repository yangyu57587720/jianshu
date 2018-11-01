"""获取数据的逻辑模块"""
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from jianshu_spider.items import JianshuSpiderItem


class JsSpider(CrawlSpider):
    # start.py启动时需要用到，名字必须是唯一的
    name = 'js'
    # 允许的域名，限制爬虫的范围
    allowed_domains = ['jianshu.com']
    # 开始的url
    start_urls = ['https://jianshu.com/']
    # 爬取的具体规则*
    rules = (
        #                  # 具体匹配正则                      # 响应回调的函数          # 循环爬取符合规则的全栈数据
        Rule(LinkExtractor(allow=r'.*/p/[0-9a-z]{12}.*'), callback='parse_detail', follow=True),
    )

    def parse_detail(self, response):
        # 页面解析，xpath语法
        title = response.xpath("//h1[@class='title']//text()").get()
        avatar = response.xpath("//a[@class='avatar']/img/@src").get()
        author = response.xpath("//span[@class='name']//text()").get()
        pub_time = response.xpath("//span[@class='publish-time']//text()").get()
        url = response.url
        article_id = url.split("?")[0].split("/")[-1]
        content = response.xpath("//div[@class='show-content']").get()
        word_count = response.xpath("//span[@class='wordage']/text()").get()
        read_count = response.xpath("//span[@class='views-count']/text()").get()
        comment_count = response.xpath("//span[@class='comments-count']/text()").get()
        like_count = response.xpath("//span[@class='likes-count']/text()").get()
        subjects = ",".join(response.xpath("//div[@class='include-collection']/a/div/text()").getall())
        # 引用模型传递数据
        item = JianshuSpiderItem(
            title=title,
            content=content,
            article_id=article_id,
            origin_url=url,
            author=author,
            avatar=avatar,
            pub_time=pub_time,
            word_count=word_count,
            read_count=read_count,
            comment_count=comment_count,
            like_count=like_count,
            subjects=subjects
        )
        # 跟return item一样
        yield item