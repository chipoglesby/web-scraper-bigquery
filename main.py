# MIT License
#
# Copyright (c) 2018 Simo Ahava
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import scrapy
import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class Page(scrapy.Item):
    crawl_start = scrapy.Field()
    url = scrapy.Field()
    status = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    crawl_time = scrapy.Field()
    since_start = scrapy.Field()


class MySpider(CrawlSpider):
    name = 'simoahava.com'
    start_time = datetime.datetime.now()
    start_time_string = datetime.datetime.utcnow().isoformat()[:-3] + 'Z'
    previous_time = datetime.datetime.now()

    allowed_domains = [
        'simoahava.com'
    ]
    start_urls = [
        'https://www.simoahava.com/'
    ]

    rules = [
        Rule(LinkExtractor(deny=('index\.xml', )), callback='parse_item', follow=True)
    ]

    def parse_item(self, response):
        self.logger.info('Scraping page %s', response.url)
        now = datetime.datetime.now()
        time_delta = now - self.start_time
        time_delta_total = int(time_delta.seconds * 1000 + time_delta.microseconds / 1000)
        time_delta_previous = now - self.previous_time
        time_delta_previous_total = int(time_delta_previous.seconds * 1000 + time_delta_previous.microseconds / 1000)
        self.previous_time = now
        item = Page(
            crawl_start=self.start_time_string,
            url=response.url,
            status=response.status,
            title=response.css('title::text').extract_first(),
            description=response.css('meta[name="description"]::attr(content)').extract_first(),
            crawl_time=time_delta_previous_total,
            since_start=time_delta_total
        )
        return item


def init_scrape(data, context):
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1',
        'FEED_FORMAT': 'jsonlines',
        'FEED_URI': './temp.json',
        'LOG_LEVEL': 'INFO'
    })

    process.crawl(MySpider)
    process.start()
