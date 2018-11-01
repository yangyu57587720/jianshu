"""替换掉系统的Download，借助selenium，下载Ajax异步请求"""
import time
from selenium import webdriver
from scrapy.http.response.html import HtmlResponse


class SeleniumDownloadMiddleware(object):

    def __init__(self):
        # 实例化路径
        self.driver = webdriver.Chrome(executable_path=r"E:\Program Files\chromedriver.exe")

    def process_request(self, request, spider):
        # 开始请求
        self.driver.get(request.url)
        time.sleep(1)
        try:
            while True:
                # 循环找到获取更多精彩内容
                more = self.driver.find_element_by_class_name("more")
                more.click()
                time.sleep(1)
                if not more:
                    break
        except:
            pass
        # 获取找到页面的源码
        source = self.driver.page_source
        # 封装当前url，源码和请求信息，编码形式
        response = HtmlResponse(url=self.driver.current_url, body=source, request=request, encoding="utf-8")
        # 截获这个请求把响应的数据返回回去
        return response