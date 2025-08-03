"""
News Spider for scraping articles from various news sources
"""

import scrapy
from news_scraper.items import NewsArticleItem
from datetime import datetime


class NewsSpider(scrapy.Spider):
    name = 'news_spider'
    
    def __init__(self, urls=None, *args, **kwargs):
        super(NewsSpider, self).__init__(*args, **kwargs)
        # Accept URLs via command line parameter
        self.start_urls = urls.split(',') if urls else []
        
        if not self.start_urls:
            # Default test URLs for initial testing
            self.start_urls = [
                'https://feeds.bbci.co.uk/news/rss.xml',  # BBC News RSS
                'https://rss.cnn.com/rss/edition.rss',    # CNN RSS
            ]
            self.logger.info("No URLs provided, using default test RSS feeds")
    
    def parse(self, response):
        """
        Parse the response and extract article data
        This method handles both RSS feeds and regular web pages
        """
        
        # Check if this is an RSS feed
        if 'xml' in response.headers.get('content-type', b'').decode().lower() or response.url.endswith('.xml'):
            yield from self.parse_rss_feed(response)
        else:
            yield from self.parse_webpage(response)
    
    def parse_rss_feed(self, response):
        """Parse RSS feed and extract article URLs"""
        
        self.logger.info(f"Parsing RSS feed: {response.url}")
        
        # Extract all item links from RSS feed
        item_links = response.css('item link::text').getall()
        if not item_links:
            # Try alternative RSS formats
            item_links = response.css('entry link::attr(href)').getall()
        
        self.logger.info(f"Found {len(item_links)} articles in RSS feed")
        
        # Follow each article link
        for link in item_links[:10]:  # Limit to first 10 for testing
            if link and link.startswith('http'):
                yield scrapy.Request(
                    url=link.strip(),
                    callback=self.parse_webpage,
                    meta={'from_rss': True}
                )
    
    def parse_webpage(self, response):
        """Parse individual article webpage"""
        
        self.logger.info(f"Parsing article: {response.url}")
        
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
                if title and len(title) > 10:  # Basic validation
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
        
        article['publication_date'] = pub_date or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
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
                # Take first 2-3 meaningful paragraphs
                for p in paragraphs[:3]:
                    clean_p = p.strip()
                    if clean_p and len(clean_p) > 20:  # Filter out short/empty paragraphs
                        summary_parts.append(clean_p)
                if summary_parts:
                    break
        
        # Create summary
        if summary_parts:
            summary = ' '.join(summary_parts)
            # Limit summary length
            if len(summary) > 500:
                summary = summary[:500] + '...'
        else:
            summary = f"Article from {response.url}"
        
        article['summary'] = summary
        
        # Log what we extracted
        self.logger.info(f"Extracted article: {article['title'][:50]}...")
        
        yield article