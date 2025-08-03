# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os
from datetime import datetime
from sqlalchemy import create_engine, Table, Column, Integer, String, DateTime, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from itemadapter import ItemAdapter


class DatabasePipeline:
    """Pipeline for saving scraped articles to PostgreSQL database with deduplication"""
    
    def __init__(self):
        # Get database URL from environment or use Neon directly
        import os
        self.database_url = os.environ.get('DATABASE_URL', 
            'postgresql://neondb_owner:npg_hTG0yxr7VbjJ@ep-shiny-lab-a2dv9n4n-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require')
        
        # Initialize database connection
        self.engine = create_engine(self.database_url)
        self.metadata = MetaData()
        
        # Define articles table schema
        self.articles_table = Table('articles', self.metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('url', String, unique=True, nullable=False),
            Column('title', String, nullable=False),
            Column('publication_date', DateTime, nullable=True),
            Column('summary', String, nullable=True)
        )
        
        # Create tables if they don't exist
        self.metadata.create_all(self.engine)
        
        # Create session
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def process_item(self, item, spider):
        """Process each scraped item and save to database"""
        adapter = ItemAdapter(item)
        
        try:
            # Prepare article data
            article_data = {
                'url': adapter.get('url'),
                'title': adapter.get('title'),
                'publication_date': self._parse_date(adapter.get('publication_date')),
                'summary': adapter.get('summary')
            }
            
            # Validate required fields
            if not article_data['url'] or not article_data['title']:
                spider.logger.warning(f"Skipping item with missing required fields: {article_data}")
                return item
            
            # Attempt to insert article
            insert_stmt = self.articles_table.insert().values(**article_data)
            self.session.execute(insert_stmt)
            self.session.commit()
            
            spider.logger.info(f"Successfully saved article: {article_data['url']}")
            
        except IntegrityError as e:
            # Handle duplicate URL (expected behavior)
            self.session.rollback()
            spider.logger.info(f"Duplicate article found (skipped): {adapter.get('url')}")
            
        except Exception as e:
            # Handle other database errors
            self.session.rollback()
            spider.logger.error(f"Failed to save article to database: {e}")
            spider.logger.error(f"Article data: {adapter.get('url', 'No URL')}")
        
        return item
    
    def _parse_date(self, date_string):
        """Parse publication date string to datetime object"""
        if not date_string:
            return None
            
        try:
            # Try common date formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
                try:
                    return datetime.strptime(date_string.strip(), fmt)
                except ValueError:
                    continue
            
            # If no format matches, return current time
            return datetime.now()
            
        except Exception:
            return datetime.now()
    
    def close_spider(self, spider):
        """Clean up database connection when spider closes"""
        self.session.close()
        spider.logger.info("Database connection closed")


class NewsScraperPipeline:
    """Legacy pipeline - kept for compatibility"""
    def process_item(self, item, spider):
        return item
