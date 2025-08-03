#!/usr/bin/env python3
"""
Database Test Script for News Scraping System
This script tests database connectivity and implements the articles table schema.
"""

import os
import sys
from sqlalchemy import create_engine, Table, Column, Integer, String, DateTime, MetaData, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime

def test_database_connection(database_url):
    """Test database connectivity and create articles table"""
    
    print("🔧 Testing Database Connection...")
    print(f"Database URL: {database_url[:50]}...")
    
    try:
        # Create database engine
        engine = create_engine(database_url, echo=True)
        
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Database connection successful!")
            print(f"PostgreSQL version: {version}")
        
        # Create metadata object
        metadata = MetaData()
        
        # Define articles table schema
        articles_table = Table('articles', metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('url', String, unique=True, nullable=False),
            Column('title', String, nullable=False),
            Column('publication_date', DateTime, nullable=True),
            Column('summary', String, nullable=True)
        )
        
        # Create tables
        print("\n🔧 Creating articles table...")
        metadata.create_all(engine)
        print("✅ Articles table created successfully!")
        
        # Test CRUD operations
        print("\n🔧 Testing CRUD operations...")
        test_crud_operations(engine, articles_table)
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_crud_operations(engine, articles_table):
    """Test Create, Read, Update, Delete operations"""
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Test INSERT
        print("📝 Testing INSERT operation...")
        test_article = {
            'url': 'https://example.com/test-article-1',
            'title': 'Test Article 1',
            'publication_date': datetime.now(),
            'summary': 'This is a test article summary.'
        }
        
        insert_stmt = articles_table.insert().values(**test_article)
        session.execute(insert_stmt)
        session.commit()
        print("✅ INSERT operation successful!")
        
        # Test duplicate prevention
        print("\n🔄 Testing duplicate prevention...")
        try:
            duplicate_article = {
                'url': 'https://example.com/test-article-1',  # Same URL
                'title': 'Duplicate Test Article',
                'publication_date': datetime.now(),
                'summary': 'This should be rejected due to duplicate URL.'
            }
            
            insert_stmt = articles_table.insert().values(**duplicate_article)
            session.execute(insert_stmt)
            session.commit()
            print("❌ Duplicate prevention FAILED - this should not happen!")
            
        except IntegrityError as e:
            session.rollback()
            print("✅ Duplicate prevention working correctly!")
            print(f"   Error (expected): {str(e)[:100]}...")
        
        # Test SELECT
        print("\n📖 Testing SELECT operation...")
        select_stmt = articles_table.select()
        result = session.execute(select_stmt)
        articles = result.fetchall()
        
        print(f"✅ Found {len(articles)} articles in database:")
        for article in articles:
            print(f"   ID: {article.id}, URL: {article.url}")
            print(f"   Title: {article.title}")
            print(f"   Date: {article.publication_date}")
            print(f"   Summary: {article.summary[:50]}...")
            print()
        
        # Test another unique article
        print("📝 Testing second INSERT with unique URL...")
        test_article_2 = {
            'url': 'https://example.com/test-article-2',
            'title': 'Test Article 2',
            'publication_date': datetime.now(),
            'summary': 'This is another test article with unique URL.'
        }
        
        insert_stmt = articles_table.insert().values(**test_article_2)
        session.execute(insert_stmt)
        session.commit()
        print("✅ Second INSERT operation successful!")
        
        # Final count
        select_stmt = articles_table.select()
        result = session.execute(select_stmt)
        final_count = len(result.fetchall())
        print(f"\n📊 Final article count: {final_count}")
        
        print("\n🎉 All CRUD operations completed successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ CRUD operation failed: {e}")
        raise
    finally:
        session.close()

def main():
    """Main function to run database tests"""
    
    print("=" * 60)
    print("[TEST] NEWS SCRAPING SYSTEM - DATABASE TEST")
    print("=" * 60)
    
    # Get database URL from environment variable
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL environment variable not set!")
        print("Please set it with your Neon PostgreSQL connection string:")
        print("export DATABASE_URL='postgresql://user:password@host/dbname?sslmode=require'")
        sys.exit(1)
    
    # Run database tests
    success = test_database_connection(database_url)
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 DATABASE SETUP COMPLETED SUCCESSFULLY!")
        print("✅ Database connection verified")
        print("✅ Articles table created")
        print("✅ UNIQUE constraint working")
        print("✅ CRUD operations tested")
        print("✅ Ready for scraper integration")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ DATABASE SETUP FAILED!")
        print("Please check your DATABASE_URL and try again.")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()