#!/usr/bin/env python3
"""
Add batch tracking to database for hourly news organization
"""

import os
import sys
from sqlalchemy import create_engine, text
from datetime import datetime

def add_batch_tracking(database_url):
    """Add batch tracking columns to articles table"""
    
    print("[BATCH TRACKING] Adding hourly batch tracking to database...")
    print(f"Database URL: {database_url[:50]}...")
    
    try:
        # Create database engine
        engine = create_engine(database_url)
        
        # Define schema updates for batch tracking
        batch_updates = [
            # Add scraping_batch_id for grouping articles by scraping session
            "ALTER TABLE articles ADD COLUMN IF NOT EXISTS scraping_batch_id VARCHAR(50)",
            
            # Add scraping_session_start timestamp for when the batch started
            "ALTER TABLE articles ADD COLUMN IF NOT EXISTS scraping_session_start TIMESTAMP",
            
            # Add articles_in_batch count for how many articles in this batch
            "ALTER TABLE articles ADD COLUMN IF NOT EXISTS articles_in_batch INTEGER DEFAULT 0",
            
            # Add scraping_run_number for sequential numbering
            "ALTER TABLE articles ADD COLUMN IF NOT EXISTS scraping_run_number INTEGER",
            
            # Create index on batch_id for fast hourly queries
            "CREATE INDEX IF NOT EXISTS idx_articles_batch_id ON articles(scraping_batch_id)",
            
            # Create index on session_start for hourly sorting
            "CREATE INDEX IF NOT EXISTS idx_articles_session_start ON articles(scraping_session_start DESC)",
            
            # Create index on run_number for sequential access
            "CREATE INDEX IF NOT EXISTS idx_articles_run_number ON articles(scraping_run_number DESC)"
        ]
        
        with engine.connect() as connection:
            # Test connection first
            result = connection.execute(text("SELECT COUNT(*) FROM articles"))
            current_count = result.scalar()
            print(f"[INFO] Current articles in database: {current_count}")
            
            # Apply each batch tracking update
            for i, update_sql in enumerate(batch_updates, 1):
                print(f"[UPDATE {i}/{len(batch_updates)}] {update_sql}")
                try:
                    connection.execute(text(update_sql))
                    connection.commit()
                    print(f"[SUCCESS] Batch update {i} completed")
                except Exception as e:
                    print(f"[INFO] Batch update {i} skipped (already exists): {e}")
            
            # Verify new schema
            print("\n[VERIFY] Checking updated table structure for batch tracking...")
            result = connection.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'articles' 
                AND column_name LIKE '%batch%' OR column_name LIKE '%session%' OR column_name LIKE '%run%'
                ORDER BY ordinal_position
            """))
            
            batch_columns = result.fetchall()
            print("[BATCH SCHEMA] New batch tracking columns:")
            print("-" * 60)
            for col in batch_columns:
                print(f"  {col.column_name:25} | {col.data_type:15} | Nullable: {col.is_nullable}")
            print("-" * 60)
            
            # Update existing records with default batch info
            print("\n[UPDATE] Setting batch info for existing records...")
            
            # Create a default batch for existing articles
            default_batch_id = f"legacy_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            default_session_start = datetime.now()
            
            update_legacy = text("""
                UPDATE articles 
                SET scraping_batch_id = :batch_id,
                    scraping_session_start = :session_start,
                    scraping_run_number = 0,
                    articles_in_batch = (SELECT COUNT(*) FROM articles WHERE scraping_batch_id IS NULL)
                WHERE scraping_batch_id IS NULL
            """)
            
            result = connection.execute(update_legacy, {
                "batch_id": default_batch_id,
                "session_start": default_session_start
            })
            updated_count = result.rowcount
            connection.commit()
            print(f"[SUCCESS] Updated {updated_count} legacy articles with batch info")
            
            # Show batch statistics
            print("\n[STATS] Current batch statistics:")
            result = connection.execute(text("""
                SELECT 
                    scraping_batch_id,
                    scraping_session_start,
                    COUNT(*) as articles_count,
                    MIN(scraped_at) as first_article,
                    MAX(scraped_at) as last_article
                FROM articles 
                WHERE scraping_batch_id IS NOT NULL
                GROUP BY scraping_batch_id, scraping_session_start
                ORDER BY scraping_session_start DESC
                LIMIT 5
            """))
            
            batch_stats = result.fetchall()
            for batch in batch_stats:
                print(f"  Batch: {batch.scraping_batch_id}")
                print(f"    Session Start: {batch.scraping_session_start}")
                print(f"    Articles: {batch.articles_count}")
                print(f"    Time Range: {batch.first_article} to {batch.last_article}")
                print()
        
        print("\n[SUCCESS] Batch tracking added successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to add batch tracking: {e}")
        return False

def main():
    """Main function to add batch tracking"""
    
    print("=" * 80)
    print("[BATCH TRACKING] NEWS SCRAPING SYSTEM - HOURLY BATCH TRACKING")
    print("=" * 80)
    
    # Get database URL from environment variable
    database_url = os.environ.get('DATABASE_URL', 
        'postgresql://neondb_owner:npg_hTG0yxr7VbjJ@ep-shiny-lab-a2dv9n4n-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require')
    
    # Set environment variable if not set
    if 'DATABASE_URL' not in os.environ:
        os.environ['DATABASE_URL'] = database_url
    
    # Add batch tracking
    success = add_batch_tracking(database_url)
    
    if success:
        print("\n" + "=" * 80)
        print("[SUCCESS] BATCH TRACKING SETUP COMPLETED!")
        print("[ADDED] scraping_batch_id column (groups articles by session)")
        print("[ADDED] scraping_session_start column (when batch started)")
        print("[ADDED] articles_in_batch column (batch size)")
        print("[ADDED] scraping_run_number column (sequential numbering)")
        print("[ADDED] Performance indexes for hourly queries")
        print("[UPDATED] Existing articles with legacy batch info")
        print("=" * 80)
        print("[READY] Database ready for hourly organized news scraping!")
    else:
        print("\n" + "=" * 80)
        print("[ERROR] BATCH TRACKING SETUP FAILED!")
        print("Please check the error messages above and try again.")
        print("=" * 80)
        sys.exit(1)

if __name__ == "__main__":
    main()