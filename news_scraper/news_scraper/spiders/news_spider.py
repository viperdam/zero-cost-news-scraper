"""
News Spider for scraping articles from various news sources
"""

import scrapy
from news_scraper.items import NewsArticleItem
from datetime import datetime
from urllib.parse import urlparse
import re


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
        
        # Extract publication date with comprehensive selectors
        pub_date = self.extract_publication_date(response)
        article['publication_date'] = pub_date
        
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
        
        # Extract full content
        content = self.extract_full_content(response)
        article['content'] = content
        
        # Extract source from URL
        article['source'] = self.extract_source(response.url)
        
        # Extract author
        article['author'] = self.extract_author(response)
        
        # Extract category
        article['category'] = self.extract_category(response)
        
        # Log what we extracted
        self.logger.info(f"Extracted article: {article['title'][:50]}... from {article['source']}")
        
        yield article
    
    def extract_full_content(self, response):
        """Extract full article content"""
        
        content_selectors = [
            '.article-body',
            '.content',
            'article',
            '.story-body',
            '.post-content',
            '.entry-content',
            '.article-content',
            '.story',
            '[data-component="text-block"]',
            '.article-text'
        ]
        
        content_parts = []
        
        for selector in content_selectors:
            content_elements = response.css(f'{selector} p::text').getall()
            if content_elements:
                for element in content_elements:
                    clean_text = element.strip()
                    if clean_text and len(clean_text) > 30:  # Filter meaningful paragraphs
                        content_parts.append(clean_text)
                if content_parts:
                    break
        
        # If no structured content found, try general paragraph extraction
        if not content_parts:
            all_paragraphs = response.css('p::text').getall()
            for p in all_paragraphs:
                clean_p = p.strip()
                if clean_p and len(clean_p) > 50:  # Longer paragraphs likely to be content
                    content_parts.append(clean_p)
                if len(content_parts) >= 10:  # Limit to avoid noise
                    break
        
        full_content = '\n\n'.join(content_parts) if content_parts else 'Content extraction failed'
        
        # Limit content length to prevent database issues
        if len(full_content) > 10000:
            full_content = full_content[:10000] + '... [Content truncated]'
        
        return full_content
    
    def extract_source(self, url):
        """Extract news source from URL"""
        
        domain = urlparse(url).netloc.lower()
        
        # Map domains to readable source names
        source_mapping = {
            'bbc.com': 'BBC',
            'bbc.co.uk': 'BBC', 
            'cnn.com': 'CNN',
            'theguardian.com': 'Guardian',
            'reuters.com': 'Reuters',
            'apnews.com': 'AP News',
            'npr.org': 'NPR',
            'techcrunch.com': 'TechCrunch',
            'news.google.com': 'Google News',
            'feeds.bbci.co.uk': 'BBC'
        }
        
        # Check for exact matches
        for domain_key, source_name in source_mapping.items():
            if domain_key in domain:
                return source_name
        
        # Extract main domain if no exact match
        domain_parts = domain.split('.')
        if len(domain_parts) >= 2:
            main_domain = domain_parts[-2].title()  # e.g., 'example' from 'www.example.com'
            return main_domain
        
        return 'Unknown'
    
    def extract_author(self, response):
        """Extract article author"""
        
        author_selectors = [
            '.author::text',
            '.byline::text',
            '[rel="author"]::text',
            '.article-author::text',
            'meta[name="author"]::attr(content)',
            '[property="article:author"]::attr(content)',
            '.writer::text',
            '.journalist::text'
        ]
        
        for selector in author_selectors:
            author = response.css(selector).get()
            if author:
                author = author.strip()
                # Clean up common prefixes
                author = re.sub(r'^(by\s+|author:\s*)', '', author, flags=re.IGNORECASE)
                if author and len(author) > 2:
                    return author
        
        return None
    
    def extract_publication_date(self, response):
        """Extract publication date with comprehensive selectors for all sources"""
        
        # Get domain to use specific extraction methods
        domain = urlparse(response.url).netloc.lower()
        
        # Try RSS pubDate first (most reliable)
        rss_date = self.extract_rss_pubdate(response)
        if rss_date:
            return rss_date
        
        # Domain-specific date extraction
        if 'cnn.com' in domain:
            return self.extract_cnn_date(response)
        elif 'theguardian.com' in domain:
            return self.extract_guardian_date(response)
        elif 'bbc.com' in domain or 'bbc.co.uk' in domain:
            return self.extract_bbc_date(response)
        elif 'reuters.com' in domain:
            return self.extract_reuters_date(response)
        elif 'nytimes.com' in domain:
            return self.extract_nyt_date(response)
        elif 'washingtonpost.com' in domain:
            return self.extract_wapo_date(response)
        elif 'npr.org' in domain:
            return self.extract_npr_date(response)
        
        # General date extraction as fallback
        return self.extract_general_date(response)
    
    def extract_rss_pubdate(self, response):
        """Extract date from RSS feed data (if available)"""
        # This would be populated if we parsed RSS with dates
        # For now, return None - could be enhanced later
        return None
    
    def extract_cnn_date(self, response):
        """Extract publication date from CNN articles"""
        selectors = [
            'meta[name="pubdate"]::attr(content)',
            'meta[property="article:published_time"]::attr(content)',
            'time[datetime]::attr(datetime)',
            '.timestamp::text',
            '.byline__date::text'
        ]
        
        for selector in selectors:
            date_str = response.css(selector).get()
            if date_str:
                parsed_date = self.parse_date_string(date_str.strip())
                if parsed_date:
                    return parsed_date
        return None
    
    def extract_guardian_date(self, response):
        """Extract publication date from Guardian articles"""
        selectors = [
            'meta[property="article:published_time"]::attr(content)',
            'time[datetime]::attr(datetime)',
            '.dcr-u0h1qy::text',  # Guardian's date class
            '.content__dateline time::attr(datetime)',
            'time::attr(datetime)'
        ]
        
        for selector in selectors:
            date_str = response.css(selector).get()
            if date_str:
                parsed_date = self.parse_date_string(date_str.strip())
                if parsed_date:
                    return parsed_date
        return None
    
    def extract_bbc_date(self, response):
        """Extract publication date from BBC articles"""
        selectors = [
            'meta[property="article:published_time"]::attr(content)',
            'time[datetime]::attr(datetime)',
            '.date::text',
            '.gel-long-primer-bold::text',
            'meta[name="OriginalPublicationDate"]::attr(content)'
        ]
        
        for selector in selectors:
            date_str = response.css(selector).get()
            if date_str:
                parsed_date = self.parse_date_string(date_str.strip())
                if parsed_date:
                    return parsed_date
        return None
    
    def extract_reuters_date(self, response):
        """Extract publication date from Reuters articles"""
        selectors = [
            'meta[property="article:published_time"]::attr(content)',
            'time[datetime]::attr(datetime)',
            '.ArticleHeader_date::text',
            '.timestamp::text'
        ]
        
        for selector in selectors:
            date_str = response.css(selector).get()
            if date_str:
                parsed_date = self.parse_date_string(date_str.strip())
                if parsed_date:
                    return parsed_date
        return None
    
    def extract_nyt_date(self, response):
        """Extract publication date from New York Times articles"""
        selectors = [
            'meta[property="article:published_time"]::attr(content)',
            'time[datetime]::attr(datetime)',
            '.css-15yh6ag::text',  # NYT date class
            '.dateline::text'
        ]
        
        for selector in selectors:
            date_str = response.css(selector).get()
            if date_str:
                parsed_date = self.parse_date_string(date_str.strip())
                if parsed_date:
                    return parsed_date
        return None
    
    def extract_wapo_date(self, response):
        """Extract publication date from Washington Post articles"""
        selectors = [
            'meta[property="article:published_time"]::attr(content)',
            'time[datetime]::attr(datetime)',
            '.timestamp::text'
        ]
        
        for selector in selectors:
            date_str = response.css(selector).get()
            if date_str:
                parsed_date = self.parse_date_string(date_str.strip())
                if parsed_date:
                    return parsed_date
        return None
    
    def extract_npr_date(self, response):
        """Extract publication date from NPR articles"""
        selectors = [
            'meta[property="article:published_time"]::attr(content)',
            'time[datetime]::attr(datetime)',
            '.dateblock time::attr(datetime)',
            '.dateline::text'
        ]
        
        for selector in selectors:
            date_str = response.css(selector).get()
            if date_str:
                parsed_date = self.parse_date_string(date_str.strip())
                if parsed_date:
                    return parsed_date
        return None
    
    def extract_general_date(self, response):
        """General date extraction for any news site"""
        selectors = [
            'meta[property="article:published_time"]::attr(content)',
            'meta[name="article:published_time"]::attr(content)',
            'meta[property="article:published"]::attr(content)',
            'meta[name="publish-date"]::attr(content)',
            'meta[name="date"]::attr(content)',
            'time[datetime]::attr(datetime)',
            'time::attr(datetime)',
            '.published::text',
            '.date::text',
            '.timestamp::text',
            '.publication-date::text',
            '.article-date::text'
        ]
        
        for selector in selectors:
            date_str = response.css(selector).get()
            if date_str:
                parsed_date = self.parse_date_string(date_str.strip())
                if parsed_date:
                    return parsed_date
        
        # If no date found, use current time as fallback
        return datetime.now()
    
    def parse_date_string(self, date_str):
        """Parse various date string formats into datetime object"""
        if not date_str:
            return None
        
        # Common date formats to try
        formats = [
            '%Y-%m-%dT%H:%M:%S.%fZ',      # ISO format with microseconds
            '%Y-%m-%dT%H:%M:%SZ',         # ISO format
            '%Y-%m-%dT%H:%M:%S%z',        # ISO with timezone
            '%Y-%m-%d %H:%M:%S',          # Standard format
            '%Y-%m-%d',                   # Date only
            '%B %d, %Y',                  # "January 15, 2025"
            '%b %d, %Y',                  # "Jan 15, 2025"
            '%d %B %Y',                   # "15 January 2025"
            '%d %b %Y',                   # "15 Jan 2025"
            '%Y/%m/%d',                   # "2025/01/15"
            '%m/%d/%Y',                   # "01/15/2025"
            '%d/%m/%Y'                    # "15/01/2025"
        ]
        
        # Clean the date string
        date_str = re.sub(r'\s+', ' ', date_str).strip()
        
        # Try parsing with each format
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # Try parsing with dateutil as last resort
        try:
            from dateutil import parser
            return parser.parse(date_str)
        except:
            pass
        
        # If all fails, return None
        return None
    
    def extract_category(self, response):
        """Extract article category"""
        
        category_selectors = [
            '.category::text',
            '.section::text',
            '.topic::text',
            'meta[name="section"]::attr(content)',
            '[property="article:section"]::attr(content)',
            '.breadcrumb a::text'
        ]
        
        for selector in category_selectors:
            category = response.css(selector).get()
            if category:
                category = category.strip().title()
                if category and len(category) > 1:
                    return category
        
        # Try to extract from URL path
        url_parts = response.url.split('/')
        for part in url_parts:
            if part in ['news', 'politics', 'business', 'tech', 'world', 'sport', 'entertainment']:
                return part.title()
        
        return None