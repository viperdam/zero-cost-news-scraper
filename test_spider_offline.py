#!/usr/bin/env python3
"""
Test the news spider offline without database
"""

import sys
import os

# Add the news_scraper directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'news_scraper'))

import scrapy
from scrapy.crawler import CrawlerProcess
from news_scraper.items import NewsArticleItem

class TestSpider(scrapy.Spider):
    name = 'test_spider'
    
    def __init__(self, urls=None, *args, **kwargs):
        super(TestSpider, self).__init__(*args, **kwargs)
        # Test URLs from our discovery
        self.start_urls = [
            'https://www.bbc.com/news/articles/cwyep6j7z0zo?at_medium=RSS&at_campaign=rss',
        ]
    
    def parse(self, response):
        """Parse article and print results"""
        
        print(f"\n[PARSE] Processing: {response.url}")
        print(f"[STATUS] Response status: {response.status}")
        print(f"[SIZE] Content length: {len(response.body)} bytes")
        
        # Create article item
        article = NewsArticleItem()
        article['url'] = response.url
        
        # Extract title using multiple selectors
        title_selectors = [
            'h1::text',
            'title::text', 
            'h1.headline::text',
            'h1.title::text',
            '.article-title::text',
            '.headline::text',
            '[property="og:title"]::attr(content)',
            'meta[name="title"]::attr(content)'
        ]
        
        title = None
        for selector in title_selectors:
            title = response.css(selector).get()
            if title:
                title = title.strip()
                if title and len(title) > 10:
                    break
        
        article['title'] = title or f"Article from {response.url}"
        
        # Extract publication date
        date_selectors = [
            'time::attr(datetime)',
            '.publication-date::text',
            '.date::text',
            '[property="article:published_time"]::attr(content)',
            'meta[name="publish-date"]::attr(content)',
            'meta[name="date"]::attr(content)'
        ]
        
        pub_date = None
        for selector in date_selectors:
            pub_date = response.css(selector).get()
            if pub_date:
                pub_date = pub_date.strip()
                break
        
        article['publication_date'] = pub_date or "Unknown"
        
        # Extract summary from first few paragraphs
        summary_selectors = [
            '.article-body p::text',
            '.content p::text',
            'article p::text',
            '.story p::text',
            'p::text'
        ]
        
        summary_parts = []
        for selector in summary_selectors:
            paragraphs = response.css(selector).getall()
            if paragraphs:
                for p in paragraphs[:3]:
                    clean_p = p.strip()
                    if clean_p and len(clean_p) > 20:
                        summary_parts.append(clean_p)
                if summary_parts:
                    break
        
        if summary_parts:
            summary = ' '.join(summary_parts)
            if len(summary) > 300:
                summary = summary[:300] + '...'
        else:
            summary = f"Article from {response.url}"
        
        article['summary'] = summary
        
        # Print extracted data
        print(f"\n[EXTRACTED DATA]")
        print(f"Title: {article['title']}")
        print(f"Date: {article['publication_date']}")
        print(f"Summary: {article['summary'][:100]}...")
        print(f"URL: {article['url']}")
        
        yield article

def run_test():
    """Run the test spider"""
    
    print("[TEST] Starting offline spider test...")
    
    # Configure the process
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 1,
        'LOG_LEVEL': 'INFO'
    })
    
    # Run the spider
    process.crawl(TestSpider)
    process.start()

if __name__ == "__main__":
    run_test()