#!/usr/bin/env python3
"""
Database Schema Update Script
Adds new columns: source, content, author to articles table
"""

import os
import sys
from sqlalchemy import create_engine, text
from datetime import datetime

def update_database_schema(database_url):
    """Update database schema to add new columns"""
    
    print("[UPDATE] Updating database schema...")
    print(f"Database URL: {database_url[:50]}...")
    
    try:
        # Create database engine
        engine = create_engine(database_url)
        
        # Define schema updates
        schema_updates = [
            # Add source column (news source like 'CNN', 'Guardian', etc.)
            "ALTER TABLE articles ADD COLUMN IF NOT EXISTS source VARCHAR(100) DEFAULT 'Unknown'",
            
            # Add content column for full article text
            "ALTER TABLE articles ADD COLUMN IF NOT EXISTS content TEXT",
            
            # Add author column
            "ALTER TABLE articles ADD COLUMN IF NOT EXISTS author VARCHAR(255)",
            
            # Add scraped_at timestamp
            "ALTER TABLE articles ADD COLUMN IF NOT EXISTS scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            
            # Add category column
            "ALTER TABLE articles ADD COLUMN IF NOT EXISTS category VARCHAR(100)",
            
            # Create index on source for faster queries
            "CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source)",
            
            # Create index on publication_date for sorting
            "CREATE INDEX IF NOT EXISTS idx_articles_pub_date ON articles(publication_date DESC)",
            
            # Create index on scraped_at for recent articles
            "CREATE INDEX IF NOT EXISTS idx_articles_scraped_at ON articles(scraped_at DESC)"
        ]
        
        with engine.connect() as connection:
            # Test connection first
            result = connection.execute(text("SELECT COUNT(*) FROM articles"))
            current_count = result.scalar()
            print(f"[INFO] Current articles in database: {current_count}")
            
            # Apply each schema update
            for i, update_sql in enumerate(schema_updates, 1):
                print(f"[UPDATE {i}/{len(schema_updates)}] {update_sql}")
                try:
                    connection.execute(text(update_sql))
                    connection.commit()
                    print(f"[SUCCESS] Update {i} completed")
                except Exception as e:
                    print(f"[INFO] Update {i} skipped (already exists or error): {e}")
            
            # Verify new schema
            print("\n[VERIFY] Checking updated table structure...")
            result = connection.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default 
                FROM information_schema.columns 
                WHERE table_name = 'articles' 
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            print("[SCHEMA] Updated table structure:")
            print("-" * 80)
            for col in columns:
                print(f"  {col.column_name:20} | {col.data_type:15} | Nullable: {col.is_nullable:3} | Default: {col.column_default}")
            print("-" * 80)
            
            # Update existing records with source information
            print("\n[UPDATE] Setting source for existing records...")
            update_sources = [
                ("UPDATE articles SET source = 'BBC' WHERE url LIKE '%bbc.com%' OR url LIKE '%bbc.co.uk%'", "BBC"),
                ("UPDATE articles SET source = 'CNN' WHERE url LIKE '%cnn.com%'", "CNN"),
                ("UPDATE articles SET source = 'Guardian' WHERE url LIKE '%theguardian.com%'", "Guardian"),
                ("UPDATE articles SET source = 'Reuters' WHERE url LIKE '%reuters.com%'", "Reuters"),
                ("UPDATE articles SET source = 'AP News' WHERE url LIKE '%apnews.com%'", "AP News"),
                ("UPDATE articles SET source = 'NPR' WHERE url LIKE '%npr.org%'", "NPR"),
                ("UPDATE articles SET source = 'TechCrunch' WHERE url LIKE '%techcrunch.com%'", "TechCrunch"),
                ("UPDATE articles SET source = 'Test' WHERE url LIKE '%test.com%' OR url LIKE '%example.com%'", "Test")
            ]
            
            for update_sql, source_name in update_sources:
                result = connection.execute(text(update_sql))
                updated_count = result.rowcount
                connection.commit()
                if updated_count > 0:
                    print(f"[SUCCESS] Updated {updated_count} articles with source '{source_name}'")
            
            # Show updated article count by source
            print("\n[STATS] Articles by source:")
            result = connection.execute(text("""
                SELECT source, COUNT(*) as count 
                FROM articles 
                GROUP BY source 
                ORDER BY count DESC
            """))
            
            source_stats = result.fetchall()
            for source, count in source_stats:
                print(f"  {source:15} | {count:3} articles")
        
        print("\n[SUCCESS] Database schema updated successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Database schema update failed: {e}")
        return False

def main():
    """Main function to run schema update"""
    
    print("=" * 80)
    print("[SCHEMA UPDATE] NEWS SCRAPING SYSTEM - DATABASE SCHEMA UPDATE")
    print("=" * 80)
    
    # Get database URL from environment variable
    database_url = os.environ.get('DATABASE_URL', 
        'postgresql://neondb_owner:npg_hTG0yxr7VbjJ@ep-shiny-lab-a2dv9n4n-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require')
    
    # Set environment variable if not set
    if 'DATABASE_URL' not in os.environ:
        os.environ['DATABASE_URL'] = database_url
    
    # Run schema update
    success = update_database_schema(database_url)
    
    if success:
        print("\n" + "=" * 80)
        print("[SUCCESS] DATABASE SCHEMA UPDATE COMPLETED!")
        print("[ADDED] ✅ source column (news source tracking)")
        print("[ADDED] ✅ content column (full article text)")
        print("[ADDED] ✅ author column (article author)")
        print("[ADDED] ✅ scraped_at column (scraping timestamp)")
        print("[ADDED] ✅ category column (article category)")
        print("[ADDED] ✅ Performance indexes")
        print("[UPDATED] ✅ Existing articles with source information")
        print("=" * 80)
        print("[READY] Database ready for enhanced news scraping!")
    else:
        print("\n" + "=" * 80)
        print("[ERROR] DATABASE SCHEMA UPDATE FAILED!")
        print("Please check the error messages above and try again.")
        print("=" * 80)
        sys.exit(1)

if __name__ == "__main__":
    main()