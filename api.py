#!/usr/bin/env python3
"""
FastAPI application for accessing scraped news articles
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy import create_engine, Table, Column, Integer, String, DateTime, MetaData, text
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 
    'postgresql://neondb_owner:npg_hTG0yxr7VbjJ@ep-shiny-lab-a2dv9n4n-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require')

# Create database engine
engine = create_engine(DATABASE_URL)

# Create session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Pydantic models for API
class Article(BaseModel):
    id: int
    url: str
    title: str
    publication_date: Optional[datetime]
    summary: Optional[str]
    source: Optional[str]
    content: Optional[str]
    author: Optional[str]
    scraped_at: Optional[datetime]
    category: Optional[str]
    scraping_batch_id: Optional[str]
    scraping_session_start: Optional[datetime]
    articles_in_batch: Optional[int]
    scraping_run_number: Optional[int]
    
    class Config:
        from_attributes = True

class ArticleResponse(BaseModel):
    articles: List[Article]
    total: int
    page: int
    per_page: int

class HourlyBatch(BaseModel):
    batch_id: str
    session_start: datetime
    article_count: int
    run_number: int
    hours_ago: int
    sources: List[str]
    latest_article: Optional[datetime]
    
class HourlyBatchResponse(BaseModel):
    batches: List[HourlyBatch]
    total_batches: int
    total_articles: int

# FastAPI app
app = FastAPI(
    title="Zero-Cost News Scraping API",
    description="API for accessing automatically scraped and deduplicated news articles",
    version="1.0.0"
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", summary="Welcome message")
async def root():
    """Welcome message and API information"""
    return {
        "message": "Zero-Cost News Scraping API",
        "description": "Automatically scraped and deduplicated news articles from multiple sources",
        "endpoints": {
            "/articles/": "Get paginated list of articles (newest first)",
            "/articles/{id}": "Get specific article by ID",
            "/search/": "Search articles by title",
            "/sources/": "Get articles filtered by news source",
            "/stats/": "Get database statistics"
        },
        "features": {
            "multi_source": "CNN, BBC, Guardian, Reuters, AP News, NPR, TechCrunch",
            "full_content": "Complete article text extraction",
            "deduplication": "Automatic duplicate prevention",
            "real_time": "Fresh articles every hour via GitHub Actions"
        },
        "github": "https://github.com/user/news-scraper",
        "status": "operational"
    }

@app.get("/articles/", response_model=ArticleResponse, summary="Get paginated articles")
async def get_articles(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Articles per page"),
    db: Session = Depends(get_db)
):
    """Get paginated list of articles, ordered by publication date (newest first)"""
    
    try:
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get total count
        total_result = db.execute(text("SELECT COUNT(*) FROM articles"))
        total = total_result.scalar()
        
        # Get articles with pagination (newest first)
        query = text("""
            SELECT id, url, title, publication_date, summary, source, content, author, scraped_at, category
            FROM articles 
            ORDER BY COALESCE(publication_date, scraped_at) DESC, id DESC
            LIMIT :limit OFFSET :offset
        """)
        
        result = db.execute(query, {"limit": per_page, "offset": offset})
        articles = []
        
        for row in result:
            articles.append(Article(
                id=row.id,
                url=row.url,
                title=row.title,
                publication_date=row.publication_date,
                summary=row.summary,
                source=row.source,
                content=row.content,
                author=row.author,
                scraped_at=row.scraped_at,
                category=row.category
            ))
        
        return ArticleResponse(
            articles=articles,
            total=total,
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/articles/{article_id}", response_model=Article, summary="Get article by ID")
async def get_article(article_id: int, db: Session = Depends(get_db)):
    """Get a specific article by ID"""
    
    try:
        query = text("""
            SELECT id, url, title, publication_date, summary, source, content, author, scraped_at, category
            FROM articles 
            WHERE id = :article_id
        """)
        
        result = db.execute(query, {"article_id": article_id})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Article not found")
        
        return Article(
            id=row.id,
            url=row.url,
            title=row.title,
            publication_date=row.publication_date,
            summary=row.summary,
            source=row.source,
            content=row.content,
            author=row.author,
            scraped_at=row.scraped_at,
            category=row.category
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/search/", response_model=ArticleResponse, summary="Search articles")
async def search_articles(
    query: str = Query(..., min_length=3, description="Search query (minimum 3 characters)"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Articles per page"),
    db: Session = Depends(get_db)
):
    """Search articles by title using case-insensitive partial matching"""
    
    try:
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Search query with case-insensitive LIKE
        search_pattern = f"%{query}%"
        
        # Get total count of matching articles
        count_query = text("""
            SELECT COUNT(*) FROM articles 
            WHERE title ILIKE :search_pattern
        """)
        
        total_result = db.execute(count_query, {"search_pattern": search_pattern})
        total = total_result.scalar()
        
        # Get matching articles with pagination
        search_query = text("""
            SELECT id, url, title, publication_date, summary, source, content, author, scraped_at, category
            FROM articles 
            WHERE title ILIKE :search_pattern
            ORDER BY COALESCE(publication_date, scraped_at) DESC, id DESC
            LIMIT :limit OFFSET :offset
        """)
        
        result = db.execute(search_query, {
            "search_pattern": search_pattern,
            "limit": per_page,
            "offset": offset
        })
        
        articles = []
        for row in result:
            articles.append(Article(
                id=row.id,
                url=row.url,
                title=row.title,
                publication_date=row.publication_date,
                summary=row.summary,
                source=row.source,
                content=row.content,
                author=row.author,
                scraped_at=row.scraped_at,
                category=row.category
            ))
        
        return ArticleResponse(
            articles=articles,
            total=total,
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/sources/", response_model=ArticleResponse, summary="Get articles by source")
async def get_articles_by_source(
    source: str = Query(..., description="News source (e.g., 'CNN', 'BBC', 'Guardian')"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Articles per page"),
    db: Session = Depends(get_db)
):
    """Get articles filtered by news source"""
    
    try:
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get total count for this source
        count_query = text("""
            SELECT COUNT(*) FROM articles 
            WHERE source ILIKE :source_pattern
        """)
        
        source_pattern = f"%{source}%"
        total_result = db.execute(count_query, {"source_pattern": source_pattern})
        total = total_result.scalar()
        
        # Get articles from this source with pagination
        source_query = text("""
            SELECT id, url, title, publication_date, summary, source, content, author, scraped_at, category
            FROM articles 
            WHERE source ILIKE :source_pattern
            ORDER BY COALESCE(publication_date, scraped_at) DESC, id DESC
            LIMIT :limit OFFSET :offset
        """)
        
        result = db.execute(source_query, {
            "source_pattern": source_pattern,
            "limit": per_page,
            "offset": offset
        })
        
        articles = []
        for row in result:
            articles.append(Article(
                id=row.id,
                url=row.url,
                title=row.title,
                publication_date=row.publication_date,
                summary=row.summary,
                source=row.source,
                content=row.content,
                author=row.author,
                scraped_at=row.scraped_at,
                category=row.category
            ))
        
        return ArticleResponse(
            articles=articles,
            total=total,
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/latest-hour/", response_model=ArticleResponse, summary="Get latest hour articles")
async def get_latest_hour_articles(
    per_page: int = Query(20, ge=1, le=100, description="Articles per page"),
    db: Session = Depends(get_db)
):
    """Get articles from the most recent scraping session/hour"""
    
    try:
        # Get the latest batch ID
        latest_batch_query = text("""
            SELECT scraping_batch_id 
            FROM articles 
            WHERE scraping_batch_id IS NOT NULL
            ORDER BY scraping_session_start DESC 
            LIMIT 1
        """)
        
        latest_result = db.execute(latest_batch_query)
        latest_batch = latest_result.scalar()
        
        if not latest_batch:
            return ArticleResponse(articles=[], total=0, page=1, per_page=per_page)
        
        # Get all articles from latest batch
        latest_articles_query = text("""
            SELECT id, url, title, publication_date, summary, source, content, author, scraped_at, category,
                   scraping_batch_id, scraping_session_start, articles_in_batch, scraping_run_number
            FROM articles 
            WHERE scraping_batch_id = :batch_id
            ORDER BY COALESCE(publication_date, scraped_at) DESC, id DESC
            LIMIT :limit
        """)
        
        result = db.execute(latest_articles_query, {
            "batch_id": latest_batch,
            "limit": per_page
        })
        
        articles = []
        for row in result:
            articles.append(Article(
                id=row.id,
                url=row.url,
                title=row.title,
                publication_date=row.publication_date,
                summary=row.summary,
                source=row.source,
                content=row.content,
                author=row.author,
                scraped_at=row.scraped_at,
                category=row.category,
                scraping_batch_id=row.scraping_batch_id,
                scraping_session_start=row.scraping_session_start,
                articles_in_batch=row.articles_in_batch,
                scraping_run_number=row.scraping_run_number
            ))
        
        # Get total count for this batch
        count_query = text("SELECT COUNT(*) FROM articles WHERE scraping_batch_id = :batch_id")
        total_result = db.execute(count_query, {"batch_id": latest_batch})
        total = total_result.scalar()
        
        return ArticleResponse(
            articles=articles,
            total=total,
            page=1,
            per_page=per_page
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/by-hour/", response_model=HourlyBatchResponse, summary="Get articles by hourly batches")
async def get_articles_by_hour(
    hours_back: int = Query(24, ge=1, le=168, description="How many hours back to show"),
    db: Session = Depends(get_db)
):
    """Get articles organized by hourly scraping batches"""
    
    try:
        # Get batch statistics
        batch_stats_query = text("""
            SELECT 
                scraping_batch_id,
                scraping_session_start,
                COUNT(*) as article_count,
                scraping_run_number,
                ARRAY_AGG(DISTINCT source) as sources,
                MAX(scraped_at) as latest_article,
                EXTRACT(EPOCH FROM (NOW() - scraping_session_start))/3600 as hours_ago
            FROM articles 
            WHERE scraping_batch_id IS NOT NULL
            AND scraping_session_start >= NOW() - INTERVAL ':hours_back hours'
            GROUP BY scraping_batch_id, scraping_session_start, scraping_run_number
            ORDER BY scraping_session_start DESC
        """)
        
        result = db.execute(batch_stats_query, {"hours_back": hours_back})
        
        batches = []
        total_articles = 0
        
        for row in result:
            hours_ago = int(row.hours_ago) if row.hours_ago else 0
            sources = row.sources if row.sources else []
            
            batches.append(HourlyBatch(
                batch_id=row.scraping_batch_id,
                session_start=row.scraping_session_start,
                article_count=row.article_count,
                run_number=row.scraping_run_number or 0,
                hours_ago=hours_ago,
                sources=sources,
                latest_article=row.latest_article
            ))
            
            total_articles += row.article_count
        
        return HourlyBatchResponse(
            batches=batches,
            total_batches=len(batches),
            total_articles=total_articles
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/stats/", summary="Get database statistics")
async def get_stats(db: Session = Depends(get_db)):
    """Get database statistics and system information"""
    
    try:
        # Get article count
        count_result = db.execute(text("SELECT COUNT(*) FROM articles"))
        total_articles = count_result.scalar()
        
        # Get latest article date
        latest_result = db.execute(text("""
            SELECT MAX(publication_date) FROM articles 
            WHERE publication_date IS NOT NULL
        """))
        latest_date = latest_result.scalar()
        
        # Get oldest article date
        oldest_result = db.execute(text("""
            SELECT MIN(publication_date) FROM articles 
            WHERE publication_date IS NOT NULL
        """))
        oldest_date = oldest_result.scalar()
        
        # Get unique domains
        domains_result = db.execute(text("""
            SELECT COUNT(DISTINCT 
                CASE 
                    WHEN url LIKE 'http://%' THEN SPLIT_PART(SPLIT_PART(url, '://', 2), '/', 1)
                    WHEN url LIKE 'https://%' THEN SPLIT_PART(SPLIT_PART(url, '://', 2), '/', 1)
                    ELSE 'unknown'
                END
            ) FROM articles
        """))
        unique_domains = domains_result.scalar()
        
        return {
            "total_articles": total_articles,
            "latest_article_date": latest_date,
            "oldest_article_date": oldest_date,
            "unique_domains": unique_domains,
            "database_status": "operational",
            "api_version": "1.0.0",
            "system": "Zero-Cost News Scraping System"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("Starting Zero-Cost News Scraping API...")
    print("Database URL configured:", DATABASE_URL[:50] + "...")
    print("API will be available at: http://localhost:8003")
    print("Interactive docs at: http://localhost:8003/docs")
    uvicorn.run(app, host="0.0.0.0", port=8003)