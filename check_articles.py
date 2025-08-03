#!/usr/bin/env python3
"""
Check articles in the database
"""

from sqlalchemy import create_engine, Table, Column, Integer, String, DateTime, MetaData, text
from sqlalchemy.orm import sessionmaker

def check_articles():
    """Check what articles are in the database"""
    
    database_url = 'postgresql://neondb_owner:npg_hTG0yxr7VbjJ@ep-shiny-lab-a2dv9n4n-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require'
    
    print("[CHECK] Checking articles in database...")
    
    try:
        engine = create_engine(database_url)
        
        # Use raw SQL to get all articles with batch tracking
        with engine.connect() as conn:
            # First, get batch statistics
            batch_result = conn.execute(text("""
                SELECT 
                    scraping_batch_id,
                    scraping_session_start,
                    scraping_run_number,
                    COUNT(*) as article_count,
                    ARRAY_AGG(DISTINCT source) as sources,
                    EXTRACT(EPOCH FROM (NOW() - scraping_session_start))/3600 as hours_ago
                FROM articles 
                WHERE scraping_batch_id IS NOT NULL
                GROUP BY scraping_batch_id, scraping_session_start, scraping_run_number
                ORDER BY scraping_session_start DESC
            """))
            batches = batch_result.fetchall()
            
            print(f"[FOUND] {len(batches)} scraping batches:")
            print("="*120)
            
            total_articles = 0
            for i, batch in enumerate(batches, 1):
                hours_ago = int(batch.hours_ago) if batch.hours_ago else 0
                time_label = "LATEST BATCH" if i == 1 else f"{hours_ago} HOURS AGO"
                
                print(f"\n[NEWS] {time_label} (Batch #{batch.scraping_run_number or 'Unknown'})")
                print(f"Batch ID: {batch.scraping_batch_id}")
                print(f"Session Start: {batch.scraping_session_start}")
                print(f"Articles: {batch.article_count} | Sources: {', '.join(batch.sources or ['Unknown'])}")
                print("-"*120)
                
                # Get articles for this batch
                articles_result = conn.execute(text("""
                    SELECT id, url, title, publication_date, summary, source, content, author, category, scraped_at 
                    FROM articles 
                    WHERE scraping_batch_id = :batch_id
                    ORDER BY COALESCE(publication_date, scraped_at) DESC
                """), {"batch_id": batch.scraping_batch_id})
                
                batch_articles = articles_result.fetchall()
                
                for j, article in enumerate(batch_articles, 1):
                    print(f"  [{j}] ID: {article.id} | SOURCE: {article.source or 'Unknown'}")
                    print(f"      TITLE: {article.title}")
                    print(f"      URL: {article.url}")
                    print(f"      DATE: {article.publication_date or article.scraped_at}")
                    if article.author:
                        print(f"      AUTHOR: {article.author}")
                    if article.category:
                        print(f"      CATEGORY: {article.category}")
                    print(f"      SUMMARY: {(article.summary or 'No summary')[:120]}...")
                    print()
                
                total_articles += batch.article_count
            
            print("="*120)
            print(f"[TOTAL] {total_articles} articles across {len(batches)} scraping sessions")
            print("="*120)
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to check articles: {e}")
        return False

if __name__ == "__main__":
    check_articles()