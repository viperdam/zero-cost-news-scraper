# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os
from datetime import datetime
from sqlalchemy import create_engine, Table, Column, Integer, String, DateTime, MetaData, Text, text
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
        
        # Generate batch ID for this scraping session
        self.batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session_start = datetime.now()
        self.batch_article_count = 0
        
        # Get next run number
        self.run_number = self._get_next_run_number()
        
        # Define articles table schema (with batch tracking)
        self.articles_table = Table('articles', self.metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('url', String, unique=True, nullable=False),
            Column('title', String, nullable=False),
            Column('publication_date', DateTime, nullable=True),
            Column('summary', String, nullable=True),
            Column('source', String, nullable=True),
            Column('content', Text, nullable=True),
            Column('author', String, nullable=True),
            Column('scraped_at', DateTime, nullable=True),
            Column('category', String, nullable=True),
            Column('scraping_batch_id', String, nullable=True),
            Column('scraping_session_start', DateTime, nullable=True),
            Column('articles_in_batch', Integer, nullable=True),
            Column('scraping_run_number', Integer, nullable=True)
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
            # Prepare article data with batch tracking
            self.batch_article_count += 1
            article_data = {
                'url': adapter.get('url'),
                'title': adapter.get('title'),
                'publication_date': self._parse_date(adapter.get('publication_date')),
                'summary': adapter.get('summary'),
                'source': adapter.get('source', 'Unknown'),
                'content': adapter.get('content'),
                'author': adapter.get('author'),
                'scraped_at': datetime.now(),
                'category': adapter.get('category'),
                'scraping_batch_id': self.batch_id,
                'scraping_session_start': self.session_start,
                'articles_in_batch': 0,  # Will be updated at end
                'scraping_run_number': self.run_number
            }
            
            # Validate required fields
            if not article_data['url'] or not article_data['title']:
                spider.logger.warning(f"Skipping item with missing required fields: {article_data}")
                return item
            
            # Attempt to insert article
            insert_stmt = self.articles_table.insert().values(**article_data)
            self.session.execute(insert_stmt)
            self.session.commit()
            
            spider.logger.info(f"[BATCH {self.batch_id}] Saved article #{self.batch_article_count} from {article_data['source']}: {article_data['title'][:50]}...")
            
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
        # Update articles_in_batch count for all articles in this batch
        try:
            update_batch_count = text("""
                UPDATE articles 
                SET articles_in_batch = :batch_count 
                WHERE scraping_batch_id = :batch_id
            """)
            
            self.session.execute(update_batch_count, {
                'batch_count': self.batch_article_count,
                'batch_id': self.batch_id
            })
            self.session.commit()
            
            spider.logger.info(f"[BATCH COMPLETE] {self.batch_id}: {self.batch_article_count} articles in batch")
            spider.logger.info(f"[SESSION] Started: {self.session_start}, Run: #{self.run_number}")
            
        except Exception as e:
            spider.logger.error(f"[ERROR] Failed to update batch count: {e}")
        
        self.session.close()
        spider.logger.info("[PIPELINE] Database connection closed")
    
    def _get_next_run_number(self):
        """Get the next sequential run number"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT COALESCE(MAX(scraping_run_number), 0) + 1 
                    FROM articles 
                    WHERE scraping_run_number IS NOT NULL
                """))
                return result.scalar() or 1
        except:
            return 1


class NewsScraperPipeline:
    """Legacy pipeline - kept for compatibility"""
    def process_item(self, item, spider):
        return item
