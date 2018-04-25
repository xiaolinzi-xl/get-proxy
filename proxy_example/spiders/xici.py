# -*- coding: utf-8 -*-

import scrapy
import json


class XiciSpider(scrapy.Spider):
    name = 'xici_proxy'
    allowed_domains = ['www.xicidaili.com']

    def start_requests(self):
        # 爬取 http://www.xicidaili.com/nn 前3页
        for i in range(0, 4):
            yield scrapy.Request('http://www.xicidaili.com/nn/%s' % i)

    def parse(self, response):
        for sel in response.css('#ip_list tr')[1:]:
            ip = sel.css('td::text').extract()[0]
            tmp = sel.css('td::text').extract()
            port = sel.css('td::text').extract()[1]
            schme = sel.css('td::text').extract()[5].lower()

            url = '%s://httpbin.org/ip' % schme
            proxy = '%s://%s:%s' % (schme, ip, port)

            meta = {
                'proxy': proxy,
                'dont_retry': True,
                'download_timeout': 10,

                '_proxy_scheme': schme,
                '_proxy_ip': ip,
            }

            yield scrapy.Request(url, callback=self.check_available, meta=meta, dont_filter=True)

    def check_available(self, response):
        proxy_ip = response.meta['_proxy_ip']

        if proxy_ip == json.loads(response.text)['origin']:
            yield {'proxy_scheme': response.meta['_proxy_scheme'], 'proxy': response.meta['proxy']}
