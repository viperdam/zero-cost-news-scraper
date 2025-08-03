#!/usr/bin/env python3
"""
Complete automation script for news scraping
This script handles the full pipeline: discovery -> scraping -> database
"""

import os
import sys
import subprocess
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def run_discovery():
    """Run the news discovery engine"""
    logger.info("Starting news URL discovery...")
    
    try:
        result = subprocess.run([
            sys.executable, 'discovery_engine.py'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            logger.info("Discovery completed successfully")
            
            # Count discovered URLs
            try:
                with open('discovered_urls.txt', 'r') as f:
                    urls = [line.strip() for line in f if line.strip()]
                logger.info(f"Discovered {len(urls)} URLs")
                return urls
            except FileNotFoundError:
                logger.warning("No discovered_urls.txt file found")
                return []
        else:
            logger.error(f"Discovery failed: {result.stderr}")
            return []
            
    except subprocess.TimeoutExpired:
        logger.error("Discovery timed out after 5 minutes")
        return []
    except Exception as e:
        logger.error(f"Discovery error: {e}")
        return []

def run_scraper(urls, max_urls=50):
    """Run the Scrapy news scraper"""
    if not urls:
        logger.warning("No URLs to scrape")
        return False
    
    # Limit URLs to prevent overwhelming the system
    urls_to_scrape = urls[:max_urls]
    url_string = ','.join(urls_to_scrape)
    
    logger.info(f"Starting scraper with {len(urls_to_scrape)} URLs...")
    
    try:
        # Change to scrapy directory and run spider
        result = subprocess.run([
            sys.executable, '-m', 'scrapy', 'crawl', 'news_spider',
            '-a', f'urls={url_string}'
        ], cwd='news_scraper', capture_output=True, text=True, timeout=1800)
        
        if result.returncode == 0:
            logger.info("Scraping completed successfully")
            
            # Extract stats from output
            output = result.stdout + result.stderr
            if "'item_scraped_count':" in output:
                # Extract item count
                for line in output.split('\n'):
                    if "'item_scraped_count':" in line:
                        try:
                            count = int(line.split("'item_scraped_count':")[1].split(',')[0].strip())
                            logger.info(f"Successfully scraped {count} items")
                        except:
                            pass
            
            return True
        else:
            logger.error(f"Scraping failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("Scraping timed out after 30 minutes")
        return False
    except Exception as e:
        logger.error(f"Scraping error: {e}")
        return False

def check_database():
    """Check database status and article count"""
    logger.info("Checking database status...")
    
    try:
        result = subprocess.run([
            sys.executable, 'check_articles.py'
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            output = result.stdout
            # Extract article count
            for line in output.split('\n'):
                if '[FOUND]' in line and 'articles in database' in line:
                    logger.info(line.strip())
            return True
        else:
            logger.error(f"Database check failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Database check error: {e}")
        return False

def main():
    """Main automation function"""
    logger.info("="*60)
    logger.info("STARTING AUTOMATED NEWS SCRAPING PIPELINE")
    logger.info("="*60)
    
    start_time = datetime.now()
    
    # Check environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL environment variable not set!")
        logger.error("Please set it with: export DATABASE_URL='your_neon_url'")
        sys.exit(1)
    
    logger.info(f"Database URL configured: {database_url[:50]}...")
    
    try:
        # Step 1: Discover URLs
        urls = run_discovery()
        if not urls:
            logger.error("No URLs discovered, exiting")
            sys.exit(1)
        
        # Step 2: Run scraper
        success = run_scraper(urls)
        if not success:
            logger.error("Scraping failed, exiting")
            sys.exit(1)
        
        # Step 3: Check results
        check_database()
        
        # Calculate runtime
        end_time = datetime.now()
        runtime = end_time - start_time
        logger.info(f"Pipeline completed successfully in {runtime}")
        
        logger.info("="*60)
        logger.info("AUTOMATED NEWS SCRAPING PIPELINE COMPLETED")
        logger.info("="*60)
        
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()