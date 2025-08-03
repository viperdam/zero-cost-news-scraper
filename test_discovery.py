#!/usr/bin/env python3
"""
Quick test of the discovery engine
"""

import feedparser

def test_simple_rss():
    """Test parsing a simple RSS feed"""
    
    print("[TEST] Testing RSS feed parsing...")
    
    # Test with a reliable RSS feed
    test_feeds = [
        'https://feeds.bbci.co.uk/news/rss.xml',
        'https://rss.cnn.com/rss/edition.rss'
    ]
    
    all_urls = []
    
    for feed_url in test_feeds:
        print(f"[PARSE] Parsing: {feed_url}")
        
        try:
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                print(f"[WARNING] Feed may be malformed: {feed.bozo_exception}")
            
            print(f"[INFO] Feed title: {feed.feed.get('title', 'Unknown')}")
            
            urls = []
            for entry in feed.entries[:10]:  # Get first 10 articles
                if hasattr(entry, 'link') and entry.link:
                    urls.append(entry.link)
                    print(f"[FOUND] {entry.get('title', 'No title')[:60]}...")
                    print(f"        {entry.link}")
            
            all_urls.extend(urls)
            print(f"[INFO] Extracted {len(urls)} URLs from this feed\n")
            
        except Exception as e:
            print(f"[ERROR] Error parsing feed: {e}\n")
    
    print(f"[COMPLETE] Total URLs discovered: {len(all_urls)}")
    
    # Save URLs for testing
    if all_urls:
        with open('test_urls.txt', 'w') as f:
            for url in all_urls:
                f.write(f"{url}\n")
        print(f"[SAVE] URLs saved to 'test_urls.txt'")
        
        # Show command to run scraper
        url_list = ','.join(all_urls[:3])  # First 3 URLs
        print(f"[CMD] Test scraper with: cd news_scraper && scrapy crawl news_spider -a urls=\"{url_list}\"")
    
    return all_urls

if __name__ == "__main__":
    test_simple_rss()