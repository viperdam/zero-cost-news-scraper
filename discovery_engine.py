#!/usr/bin/env python3
"""
News Discovery Engine
Discovers article URLs from RSS feeds and XML sitemaps
"""

import feedparser
import requests
from usp.tree import sitemap_tree_for_homepage
from urllib.parse import urljoin, urlparse
import re
from typing import List, Set


class NewsDiscovery:
    """Engine for discovering news article URLs from various sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def find_rss_feeds(self, domain: str) -> List[str]:
        """Find RSS feed URLs for a given domain"""
        
        print(f"[SEARCH] Searching for RSS feeds on {domain}")
        
        # Ensure domain has protocol
        if not domain.startswith('http'):
            domain = f'https://{domain}'
        
        feeds = []
        
        # Check common RSS feed locations
        common_rss_paths = [
            '/rss.xml',
            '/rss',
            '/feed',
            '/feed.xml',
            '/feeds/all.atom.xml',
            '/atom.xml',
            '/feeds/all.rss.xml',
            '/feeds/news.xml',
            '/news/rss.xml'
        ]
        
        for path in common_rss_paths:
            try:
                feed_url = urljoin(domain, path)
                response = self.session.head(feed_url, timeout=10)
                if response.status_code == 200:
                    # Verify it's actually a feed
                    feed_response = self.session.get(feed_url, timeout=10)
                    if self._is_valid_feed(feed_response.text):
                        feeds.append(feed_url)
                        print(f"[SUCCESS] Found RSS feed: {feed_url}")
            except Exception as e:
                print(f"[WARNING] Error checking {feed_url}: {e}")
        
        # Check robots.txt for sitemap declarations
        try:
            robots_url = urljoin(domain, '/robots.txt')
            response = self.session.get(robots_url, timeout=10)
            if response.status_code == 200:
                sitemap_urls = re.findall(r'Sitemap:\s*(.+)', response.text, re.IGNORECASE)
                for sitemap_url in sitemap_urls:
                    sitemap_url = sitemap_url.strip()
                    if sitemap_url and sitemap_url not in feeds:
                        feeds.append(sitemap_url)
                        print(f"[SUCCESS] Found sitemap in robots.txt: {sitemap_url}")
        except Exception as e:
            print(f"[WARNING] Error checking robots.txt: {e}")
        
        # Check homepage for RSS links
        try:
            response = self.session.get(domain, timeout=10)
            if response.status_code == 200:
                # Look for RSS link tags
                rss_links = re.findall(
                    r'<link[^>]*type=["\']application/rss\+xml["\'][^>]*href=["\']([^"\']+)["\'][^>]*>',
                    response.text,
                    re.IGNORECASE
                )
                for link in rss_links:
                    full_url = urljoin(domain, link)
                    if full_url not in feeds:
                        feeds.append(full_url)
                        print(f"[SUCCESS] Found RSS link in homepage: {full_url}")
        except Exception as e:
            print(f"[WARNING] Error checking homepage: {e}")
        
        print(f"[INFO] Total RSS feeds found: {len(feeds)}")
        return feeds
    
    def _is_valid_feed(self, content: str) -> bool:
        """Check if content appears to be a valid RSS/Atom feed"""
        content_lower = content.lower()
        return any(tag in content_lower for tag in ['<rss', '<feed', '<atom', '<item>', '<entry>'])
    
    def parse_rss_feed(self, feed_url: str) -> List[str]:
        """Parse RSS feed and extract article URLs"""
        
        print(f"[PARSE] Parsing RSS feed: {feed_url}")
        
        try:
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                print(f"[WARNING] Feed may be malformed: {feed.bozo_exception}")
            
            urls = []
            for entry in feed.entries[:50]:  # Limit to latest 50 articles
                if hasattr(entry, 'link') and entry.link:
                    urls.append(entry.link)
            
            print(f"[INFO] Extracted {len(urls)} URLs from RSS feed")
            return urls
            
        except Exception as e:
            print(f"[ERROR] Error parsing RSS feed {feed_url}: {e}")
            return []
    
    def get_sitemap_urls(self, domain: str) -> List[str]:
        """Extract URLs from website's XML sitemap"""
        
        print(f"[SITEMAP] Parsing sitemap for {domain}")
        
        # Ensure domain has protocol
        if not domain.startswith('http'):
            domain = f'https://{domain}'
        
        try:
            tree = sitemap_tree_for_homepage(domain)
            urls = []
            
            for page in tree.all_pages():
                # Filter for news/article URLs
                if self._is_news_url(page.url):
                    urls.append(page.url)
                
                # Limit to prevent overwhelming the system
                if len(urls) >= 100:
                    break
            
            print(f"[INFO] Extracted {len(urls)} news URLs from sitemap")
            return urls
            
        except Exception as e:
            print(f"[ERROR] Error parsing sitemap for {domain}: {e}")
            return []
    
    def _is_news_url(self, url: str) -> bool:
        """Heuristic to determine if URL likely contains a news article"""
        
        url_lower = url.lower()
        
        # News indicators
        news_patterns = [
            '/news/', '/article/', '/story/', '/post/', '/blog/',
            '/press-release/', '/announcement/', '/update/'
        ]
        
        # Skip non-article pages
        skip_patterns = [
            '/category/', '/tag/', '/author/', '/search/', '/page/',
            '/contact/', '/about/', '/privacy/', '/terms/',
            '.pdf', '.jpg', '.png', '.gif', '.css', '.js'
        ]
        
        # Check for news patterns
        has_news_pattern = any(pattern in url_lower for pattern in news_patterns)
        
        # Check for date patterns (often in news URLs)
        has_date_pattern = bool(re.search(r'/20\d{2}/', url))
        
        # Check if should skip
        should_skip = any(pattern in url_lower for pattern in skip_patterns)
        
        return (has_news_pattern or has_date_pattern) and not should_skip
    
    def discover_all_urls(self, domains: List[str]) -> List[str]:
        """Discover all article URLs from multiple domains"""
        
        print("[START] Starting comprehensive URL discovery")
        print(f"[INFO] Target domains: {domains}")
        
        all_urls = set()
        
        for domain in domains:
            print(f"\n[PROCESS] Processing domain: {domain}")
            
            # Find and parse RSS feeds
            rss_feeds = self.find_rss_feeds(domain)
            for feed_url in rss_feeds:
                urls = self.parse_rss_feed(feed_url)
                all_urls.update(urls)
            
            # Parse sitemap
            sitemap_urls = self.get_sitemap_urls(domain)
            all_urls.update(sitemap_urls)
        
        # Convert to list and remove duplicates
        unique_urls = list(all_urls)
        
        print(f"\n[COMPLETE] DISCOVERY COMPLETE")
        print(f"[SUCCESS] Total unique URLs discovered: {len(unique_urls)}")
        
        return unique_urls


def main():
    """Main function for testing the discovery engine"""
    
    # Comprehensive news sources with working RSS feeds (2025)
    rss_sources = [
        # CNN RSS feeds (working perfectly)
        'http://rss.cnn.com/rss/cnn_topstories.rss',
        'http://rss.cnn.com/rss/edition.rss',
        'http://rss.cnn.com/rss/cnn_allpolitics.rss',
        'http://rss.cnn.com/rss/money_news_economy.rss',
        'http://rss.cnn.com/rss/cnn_world.rss',
        'http://rss.cnn.com/rss/cnn_us.rss',
        
        # Guardian RSS feeds (excellent coverage)
        'https://www.theguardian.com/rss',
        'https://www.theguardian.com/world/rss',
        'https://www.theguardian.com/us-news/rss',
        'https://www.theguardian.com/uk-news/rss',
        'https://www.theguardian.com/politics/rss',
        'https://www.theguardian.com/technology/rss',
        'https://www.theguardian.com/business/rss',
        'https://www.theguardian.com/environment/rss',
        'https://www.theguardian.com/science/rss',
        
        # BBC RSS feeds (comprehensive)
        'http://feeds.bbci.co.uk/news/rss.xml',
        'http://feeds.bbci.co.uk/news/world/rss.xml',
        'http://feeds.bbci.co.uk/news/uk/rss.xml',
        'http://feeds.bbci.co.uk/news/business/rss.xml',
        'http://feeds.bbci.co.uk/news/technology/rss.xml',
        'http://feeds.bbci.co.uk/news/politics/rss.xml',
        'http://feeds.bbci.co.uk/news/health/rss.xml',
        'http://feeds.bbci.co.uk/news/science_and_environment/rss.xml',
        
        # Reuters via Google News (24h only)
        'https://news.google.com/rss/search?q=when:24h+allinurl:reuters.com&ceid=US:en&hl=en-US&gl=US',
        'https://news.google.com/rss/search?q=when:12h+allinurl:reuters.com+business&ceid=US:en&hl=en-US&gl=US',
        'https://news.google.com/rss/search?q=when:12h+allinurl:reuters.com+technology&ceid=US:en&hl=en-US&gl=US',
        
        # NPR (working feeds)
        'https://feeds.npr.org/1001/rss.xml',        # All Things Considered
        'https://feeds.npr.org/1004/rss.xml',        # Morning Edition
        'https://feeds.npr.org/1006/rss.xml',        # NPR News Now
        'https://feeds.npr.org/1019/rss.xml',        # Politics Podcast
        
        # TechCrunch (tech news)
        'https://feeds.feedburner.com/TechCrunch',
        
        # Working additional sources
        'http://feeds.washingtonpost.com/rss/world',
        'https://rss.nytimes.com/services/xml/rss/nyt/World.xml',
        'https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml',
        'https://rss.nytimes.com/services/xml/rss/nyt/Business.xml',
        
        # Financial news
        'https://feeds.finance.yahoo.com/rss/2.0/headline',
        'https://feeds.bloomberg.com/markets/news.rss',
        
        # Additional reliable sources
        'https://www.cbsnews.com/latest/rss/main',
        'https://feeds.nbcnews.com/nbcnews/public/news',
        'https://feeds.abcnews.com/abcnews/topstories',
        
        # International sources
        'https://feeds.skynews.com/feeds/rss/home.xml',
        'https://www.aljazeera.com/xml/rss/all.xml',
        
        # Science and tech
        'https://rss.cnn.com/rss/edition_technology.rss',
        'https://feeds.ars-technica.com/arstechnica/index',
        'http://feeds.reuters.com/reuters/technologyNews'
    ]
    
    discovery = NewsDiscovery()
    all_urls = []
    
    print("[START] Parsing multiple RSS feeds from major news sources")
    print("="*80)
    
    for feed_url in rss_sources:
        print(f"\n[PROCESSING] {feed_url}")
        urls = discovery.parse_rss_feed(feed_url)
        all_urls.extend(urls)
        print(f"[FOUND] {len(urls)} URLs from this feed")
    
    # Remove duplicates while preserving order
    unique_urls = []
    seen = set()
    for url in all_urls:
        if url not in seen:
            unique_urls.append(url)
            seen.add(url)
    
    print(f"\n[COMPLETE] URL DISCOVERY COMPLETE")
    print(f"[SUCCESS] Total unique URLs discovered: {len(unique_urls)}")
    print("="*80)
    
    for i, url in enumerate(unique_urls[:20], 1):  # Show first 20 URLs
        print(f"{i:2d}. {url}")
    
    if len(unique_urls) > 20:
        print(f"... and {len(unique_urls) - 20} more URLs")
    
    # Save URLs to file for scraper
    if unique_urls:
        with open('discovered_urls.txt', 'w') as f:
            for url in unique_urls:
                f.write(f"{url}\n")
        print(f"\n[SAVE] URLs saved to 'discovered_urls.txt'")
        print(f"[INFO] Ready to scrape {len(unique_urls)} articles from multiple sources!")
        
        return unique_urls


if __name__ == "__main__":
    main()