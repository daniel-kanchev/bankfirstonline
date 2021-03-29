import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bankfirstonline.items import Article


class bankfirstonlineSpider(scrapy.Spider):
    name = 'bankfirstonline'
    start_urls = ['https://bankfirstonline.com/news/']

    def parse(self, response):
        yield response.follow(response.url, self.parse_article, dont_filter=True)

        next_page = response.xpath('//a[contains(@class, "next_page")]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        articles = response.xpath('//article')
        for article in articles:
            item = ItemLoader(Article())
            item.default_output_processor = TakeFirst()

            title = article.xpath('.//h2/a/text()').get()
            if not title:
                return

            date = article.xpath('.//time/text()').get()

            content = article.xpath('.//div[@class="entry-content"]//text()').getall()
            content = [text for text in content if text.strip() and '{' not in text]
            content = "\n".join(content).strip()

            item.add_value('title', title)
            item.add_value('date', date)
            item.add_value('content', content)

            yield item.load_item()
