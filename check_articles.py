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
        
        # Use raw SQL to get all articles
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, url, title, publication_date, summary FROM articles ORDER BY id"))
            articles = result.fetchall()
            
            print(f"[FOUND] {len(articles)} articles in database:")
            print("="*80)
            
            for article in articles:
                print(f"ID: {article.id}")
                print(f"URL: {article.url}")
                print(f"Title: {article.title}")
                print(f"Date: {article.publication_date}")
                print(f"Summary: {article.summary[:100]}...")
                print("-"*80)
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to check articles: {e}")
        return False

if __name__ == "__main__":
    check_articles()