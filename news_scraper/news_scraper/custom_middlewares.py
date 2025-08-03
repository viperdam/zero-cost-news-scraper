"""
Custom middlewares for the news scraper
"""

import random


class RotateUserAgentMiddleware:
    """Middleware to rotate User-Agent headers"""
    
    # List of realistic User-Agent strings
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ]
    
    def process_request(self, request, spider):
        """Process each request and set a random User-Agent"""
        
        # Randomly select a User-Agent for the request
        user_agent = random.choice(self.USER_AGENTS)
        request.headers['User-Agent'] = user_agent
        
        # Set other realistic browser headers
        request.headers.setdefault('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8')
        request.headers.setdefault('Accept-Language', 'en-US,en;q=0.9')
        request.headers.setdefault('Accept-Encoding', 'gzip, deflate, br')
        request.headers.setdefault('Connection', 'keep-alive')
        request.headers.setdefault('Upgrade-Insecure-Requests', '1')
        request.headers.setdefault('Sec-Fetch-Dest', 'document')
        request.headers.setdefault('Sec-Fetch-Mode', 'navigate')
        request.headers.setdefault('Sec-Fetch-Site', 'none')
        request.headers.setdefault('Sec-Fetch-User', '?1')
        
        spider.logger.debug(f"Using User-Agent: {user_agent}")
        
        return None