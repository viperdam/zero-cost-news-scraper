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
    
    class Config:
        from_attributes = True

class ArticleResponse(BaseModel):
    articles: List[Article]
    total: int
    page: int
    per_page: int

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
        "description": "Automatically scraped and deduplicated news articles",
        "endpoints": {
            "/articles/": "Get paginated list of articles",
            "/articles/{id}": "Get specific article by ID",
            "/search/": "Search articles by title",
            "/stats/": "Get database statistics"
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
        
        # Get articles with pagination
        query = text("""
            SELECT id, url, title, publication_date, summary 
            FROM articles 
            ORDER BY publication_date DESC, id DESC
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
                summary=row.summary
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
            SELECT id, url, title, publication_date, summary 
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
            summary=row.summary
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
            SELECT id, url, title, publication_date, summary 
            FROM articles 
            WHERE title ILIKE :search_pattern
            ORDER BY publication_date DESC, id DESC
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
                summary=row.summary
            ))
        
        return ArticleResponse(
            articles=articles,
            total=total,
            page=page,
            per_page=per_page
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
    print("API will be available at: http://localhost:8000")
    print("Interactive docs at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)