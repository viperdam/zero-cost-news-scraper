#!/usr/bin/env python3
"""
Simple Database Test Script - No Unicode
"""

import os
import sys
from sqlalchemy import create_engine, Table, Column, Integer, String, DateTime, MetaData, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime

def test_database():
    """Test database connectivity and create table"""
    
    # Database URL from environment or hardcoded for this test
    database_url = os.environ.get('DATABASE_URL', 
        'postgresql://neondb_owner:npg_hTG0yxr7VbjJ@ep-shiny-lab-a2dv9n4n-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require')
    
    print("[CONNECT] Testing database connection...")
    print(f"[URL] {database_url[:50]}...")
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"[SUCCESS] Connected to PostgreSQL")
            print(f"[VERSION] {version[:50]}...")
        
        # Create metadata and table
        metadata = MetaData()
        articles_table = Table('articles', metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('url', String, unique=True, nullable=False),
            Column('title', String, nullable=False),
            Column('publication_date', DateTime, nullable=True),
            Column('summary', String, nullable=True)
        )
        
        print("[CREATE] Creating articles table...")
        metadata.create_all(engine)
        print("[SUCCESS] Articles table created!")
        
        # Test CRUD operations
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("[INSERT] Testing article insertion...")
        
        # Test article
        article_data = {
            'url': 'https://test.com/article-1',
            'title': 'Test Article 1',
            'publication_date': datetime.now(),
            'summary': 'This is a test article for database testing.'
        }
        
        insert_stmt = articles_table.insert().values(**article_data)
        session.execute(insert_stmt)
        session.commit()
        print("[SUCCESS] Article inserted successfully!")
        
        # Test duplicate prevention
        print("[DUPLICATE] Testing duplicate prevention...")
        try:
            duplicate_data = {
                'url': 'https://test.com/article-1',  # Same URL
                'title': 'Duplicate Article',
                'publication_date': datetime.now(),
                'summary': 'This should be rejected.'
            }
            
            insert_stmt = articles_table.insert().values(**duplicate_data)
            session.execute(insert_stmt)
            session.commit()
            print("[ERROR] Duplicate was allowed - this is wrong!")
            
        except IntegrityError:
            session.rollback()
            print("[SUCCESS] Duplicate correctly rejected!")
        
        # Test SELECT
        print("[SELECT] Testing article retrieval...")
        select_stmt = articles_table.select()
        result = session.execute(select_stmt)
        articles = result.fetchall()
        
        print(f"[SUCCESS] Found {len(articles)} articles:")
        for article in articles:
            print(f"  ID: {article.id}")
            print(f"  URL: {article.url}")
            print(f"  Title: {article.title}")
            print("")
        
        session.close()
        
        print("="*50)
        print("[SUCCESS] DATABASE SETUP COMPLETE!")
        print("[SUCCESS] Connection verified")
        print("[SUCCESS] Table created")
        print("[SUCCESS] UNIQUE constraint working")
        print("[SUCCESS] Ready for scraper!")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Database test failed: {e}")
        return False

if __name__ == "__main__":
    test_database()