# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsArticleItem(scrapy.Item):
    """Structured data container for news articles"""
    url = scrapy.Field()
    title = scrapy.Field()
    publication_date = scrapy.Field()
    summary = scrapy.Field()
