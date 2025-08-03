# 🚀 Zero-Cost News Scraping System Roadmap

## 📋 Project Overview

**Objective**: Build a fully automated, zero-cost pipeline that continuously discovers and scrapes the latest news articles, implements automatic deduplication, and serves unique news items through a simple API.

**Success Criteria**: 
- Fully automated operation with no manual intervention
- Zero operational costs (free-tier only)
- Automatic deduplication to prevent repeat entries
- Stable, continuous operation with proper error handling
- Professional-grade API for data access

---

## 🎯 PHASE 1: FOUNDATION & ARCHITECTURE
**Milestone**: System Architecture & Data Persistence

### 🔧 1.1 Database Setup & Configuration
**Goal**: Establish cloud-hosted PostgreSQL database with deduplication schema

#### ✅ Checklist:
- [ ] **CRITICAL**: Sign up for Neon free-tier PostgreSQL account
  - Visit https://neon.com and create account
  - Create new project in dashboard
  - Copy database connection URL (format: `postgresql://user:password@host/dbname?sslmode=require`)
  - **VERIFY**: Database connection works before proceeding

- [ ] **CRITICAL**: Design and implement articles table schema
  ```sql
  CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    publication_date TIMESTAMP,
    summary TEXT
  );
  ```
  - **VERIFY**: UNIQUE constraint on URL column is active
  - **VERIFY**: Test duplicate insertion rejection
  - **VERIFY**: All columns have correct data types

- [ ] **CRITICAL**: Test database connectivity and CRUD operations
  - Create test connection script
  - Insert sample article
  - Attempt duplicate insertion (should fail gracefully)
  - Query and retrieve data
  - **VERIFY**: All operations work as expected

#### 🛑 Exit Criteria:
- Database is accessible via connection string
- Articles table exists with proper schema
- Duplicate URL insertion is automatically rejected
- Basic CRUD operations confirmed working

---

## 🕷️ PHASE 2: SCRAPING ENGINE DEVELOPMENT
**Milestone**: Core Scraper Implementation with Integrated Deduplication

### 🔧 2.1 Scrapy Project Setup
**Goal**: Create scalable scraping framework with proper structure

#### ✅ Checklist:
- [ ] **CRITICAL**: Install required Python packages
  ```bash
  pip install scrapy psycopg2-binary sqlalchemy feedparser ultimate-sitemap-parser
  ```
  - **VERIFY**: All packages install successfully
  - **VERIFY**: No version conflicts

- [ ] **CRITICAL**: Initialize Scrapy project structure
  ```bash
  scrapy startproject news_scraper
  ```
  - **VERIFY**: Project directory created correctly
  - **VERIFY**: All Scrapy files present (spiders/, items.py, pipelines.py, settings.py)

- [ ] **CRITICAL**: Configure project settings for politeness
  - Enable ROBOTSTXT_OBEY = True
  - Configure AutoThrottle settings:
    ```python
    AUTOTHROTTLE_ENABLED = True
    AUTOTHROTTLE_START_DELAY = 5
    AUTOTHROTTLE_MAX_DELAY = 60
    AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
    ```
  - **VERIFY**: Settings prevent aggressive crawling

### 🔧 2.2 Data Structure & Item Definition
**Goal**: Define structured data containers for scraped content

#### ✅ Checklist:
- [ ] **CRITICAL**: Define NewsArticleItem in items.py
  ```python
  class NewsArticleItem(scrapy.Item):
      url = scrapy.Field()
      title = scrapy.Field()
      publication_date = scrapy.Field()
      summary = scrapy.Field()
  ```
  - **VERIFY**: All required fields defined
  - **VERIFY**: Field types match database schema

### 🔧 2.3 Database Integration Pipeline
**Goal**: Implement automatic data persistence with duplicate handling

#### ✅ Checklist:
- [ ] **CRITICAL**: Implement DatabasePipeline in pipelines.py
  - Create database connection using SQLAlchemy
  - Define table schema matching NewsArticleItem
  - Implement process_item method with try/except for duplicates
  - Handle IntegrityError gracefully for URL conflicts
  - **VERIFY**: Pipeline connects to database successfully
  - **VERIFY**: Duplicate handling works correctly

- [ ] **CRITICAL**: Configure pipeline in settings.py
  ```python
  ITEM_PIPELINES = {
      'news_scraper.pipelines.DatabasePipeline': 300,
  }
  DATABASE_URL = "postgresql://user:password@host/dbname?sslmode=require"
  ```
  - **VERIFY**: Pipeline is enabled and ordered correctly
  - **VERIFY**: Database URL is properly configured

### 🔧 2.4 News Spider Implementation
**Goal**: Create intelligent spider for article extraction

#### ✅ Checklist:
- [ ] **CRITICAL**: Implement news_spider.py with proper structure
  - Accept URLs via command line parameter
  - Extract title using CSS selectors
  - Extract publication date
  - Extract summary from article body
  - Yield NewsArticleItem with all fields populated
  - **VERIFY**: Spider accepts URL list correctly
  - **VERIFY**: CSS selectors extract data accurately

- [ ] **CRITICAL**: Test spider with sample URLs
  - Run: `scrapy crawl news_spider -a urls="url1,url2"`
  - **VERIFY**: Items are extracted correctly
  - **VERIFY**: Data is saved to database
  - **VERIFY**: Duplicate URLs are handled gracefully

#### 🛑 Exit Criteria:
- Scrapy project is properly configured
- DatabasePipeline successfully saves to PostgreSQL
- News spider extracts all required fields
- Duplicate articles are automatically rejected
- System operates politely with proper delays

---

## 🔍 PHASE 3: INTELLIGENT DISCOVERY ENGINE
**Milestone**: Efficient Article Discovery via RSS & Sitemaps

### 🔧 3.1 RSS Feed Discovery & Parsing
**Goal**: Implement RSS feed discovery and parsing for real-time updates

#### ✅ Checklist:
- [ ] **CRITICAL**: Create RSS feed discovery script
  - Implement function to find RSS feeds from robots.txt
  - Check common RSS URL patterns (/rss.xml, /feed, /rss)
  - Parse page HTML for RSS link tags
  - **VERIFY**: Script finds RSS feeds for target news sites

- [ ] **CRITICAL**: Implement RSS parsing with feedparser
  ```python
  import feedparser
  def parse_rss_feed(feed_url):
      feed = feedparser.parse(feed_url)
      # Extract entry URLs, titles, dates
      return article_urls
  ```
  - **VERIFY**: RSS feeds parse correctly
  - **VERIFY**: Article URLs are extracted
  - **VERIFY**: Publication dates are captured

### 🔧 3.2 Sitemap Crawling Implementation
**Goal**: Comprehensive URL discovery via XML sitemaps

#### ✅ Checklist:
- [ ] **CRITICAL**: Implement sitemap parsing with ultimate-sitemap-parser
  ```python
  from usp.tree import sitemap_tree_for_homepage
  def get_all_urls_from_sitemap(homepage_url):
      tree = sitemap_tree_for_homepage(homepage_url)
      return [page.url for page in tree.all_pages()]
  ```
  - **VERIFY**: Sitemaps are discovered automatically
  - **VERIFY**: All URLs are extracted correctly
  - **VERIFY**: Nested sitemaps are handled

- [ ] **CRITICAL**: Create URL discovery orchestrator script
  - Combine RSS and sitemap discovery
  - Deduplicate URLs across sources
  - Filter URLs to news articles only
  - Output comma-separated URL list for spider
  - **VERIFY**: Script produces clean URL list
  - **VERIFY**: URLs are relevant news articles

#### 🛑 Exit Criteria:
- RSS feeds are automatically discovered and parsed
- Sitemaps provide comprehensive URL coverage
- URL discovery script produces clean, deduplicated lists
- Discovery process is fully automated

---

## 🛡️ PHASE 4: ANTI-DETECTION & POLITENESS
**Milestone**: Implement sophisticated evasion and respectful crawling

### 🔧 4.1 User-Agent & Header Rotation
**Goal**: Implement realistic browser identity rotation

#### ✅ Checklist:
- [ ] **CRITICAL**: Create RotateUserAgentMiddleware
  - Define list of realistic User-Agent strings
  - Implement random User-Agent selection
  - Add realistic browser headers (Accept, Accept-Language, etc.)
  - Ensure header consistency with chosen User-Agent
  - **VERIFY**: Each request has different, realistic headers

- [ ] **CRITICAL**: Configure middleware in settings.py
  ```python
  DOWNLOADER_MIDDLEWARES = {
      'news_scraper.custom_middlewares.RotateUserAgentMiddleware': 543,
  }
  ```
  - **VERIFY**: Middleware is properly enabled
  - **VERIFY**: Headers rotate correctly for each request

### 🔧 4.2 Advanced Politeness Configuration
**Goal**: Ensure respectful, sustainable scraping behavior

#### ✅ Checklist:
- [ ] **CRITICAL**: Fine-tune AutoThrottle settings
  - Test with actual target websites
  - Adjust delays based on server response times
  - Monitor for any blocking or rate limiting
  - **VERIFY**: Scraping speed is conservative and respectful

- [ ] **CRITICAL**: Implement robots.txt compliance verification
  - Test ROBOTSTXT_OBEY setting with various sites
  - Manually verify robots.txt rules are followed
  - **VERIFY**: Disallowed URLs are not accessed

### 🔧 4.3 Dynamic Content Handling Strategy
**Goal**: Handle JavaScript-rendered content efficiently

#### ✅ Checklist:
- [ ] **CRITICAL**: Identify dynamic content on target sites
  - Use browser developer tools to monitor XHR/Fetch requests
  - Document API endpoints for dynamic content
  - Create list of sites requiring special handling
  - **VERIFY**: All content types are identified

- [ ] **CRITICAL**: Implement API reverse-engineering for dynamic sites
  - Replicate API calls in Scrapy requests
  - Extract data from JSON responses
  - Test API endpoint stability
  - **VERIFY**: Dynamic content is successfully extracted

#### 🛑 Exit Criteria:
- All requests use realistic, rotating browser identities
- Scraping speed is respectful and sustainable
- robots.txt compliance is verified
- Dynamic content is handled without headless browsers

---

## ⚡ PHASE 5: AUTOMATION & CONTINUOUS OPERATION
**Milestone**: Automated Scheduling & Deployment

### 🔧 5.1 GitHub Actions Workflow Setup
**Goal**: Implement scheduled, automated scraping execution

#### ✅ Checklist:
- [ ] **CRITICAL**: Create .github/workflows/scrape.yml
  - Configure cron schedule (hourly: '0 * * * *')
  - Set up Python environment
  - Install dependencies from requirements.txt
  - Execute discovery script followed by spider
  - **VERIFY**: Workflow triggers on schedule

- [ ] **CRITICAL**: Configure GitHub Secrets for security
  - Add DATABASE_URL as encrypted secret
  - Test secret injection in workflow
  - **VERIFY**: Database connection works in GitHub Actions
  - **VERIFY**: No sensitive data exposed in logs

- [ ] **CRITICAL**: Implement comprehensive error handling
  - Add email notification on workflow failure
  - Configure error logging and reporting
  - Test failure scenarios
  - **VERIFY**: Failures are detected and reported

### 🔧 5.2 Workflow Testing & Optimization
**Goal**: Ensure reliable, efficient automated execution

#### ✅ Checklist:
- [ ] **CRITICAL**: Test complete automation pipeline
  - Run full discovery-to-database cycle
  - Verify data quality and completeness
  - Check for any race conditions or timing issues
  - **VERIFY**: End-to-end automation works flawlessly

- [ ] **CRITICAL**: Optimize workflow performance
  - Minimize execution time within GitHub Actions limits
  - Implement efficient discovery algorithms
  - Test with various load scenarios
  - **VERIFY**: Workflow completes within time limits

#### 🛑 Exit Criteria:
- GitHub Actions workflow runs automatically on schedule
- Complete discovery and scraping cycle executes without intervention
- Failures are detected and reported immediately
- Performance is optimized for free-tier constraints

---

## 🌐 PHASE 6: API DEVELOPMENT & DEPLOYMENT
**Milestone**: High-Performance Data Delivery API

### 🔧 6.1 FastAPI Application Development
**Goal**: Create professional-grade API for data access

#### ✅ Checklist:
- [ ] **CRITICAL**: Install FastAPI dependencies
  ```bash
  pip install "fastapi[all]" sqlmodel psycopg2-binary uvicorn
  ```
  - **VERIFY**: All packages install correctly

- [ ] **CRITICAL**: Implement main.py with SQLModel integration
  - Define Article model matching database schema
  - Create database connection with dependency injection
  - Implement pagination support
  - Add proper error handling and HTTP status codes
  - **VERIFY**: API connects to database successfully

- [ ] **CRITICAL**: Implement core API endpoints
  - GET / (welcome message)
  - GET /articles/ (paginated article list)
  - GET /articles/{id} (single article retrieval)
  - GET /search/?query= (title search functionality)
  - **VERIFY**: All endpoints return correct data and status codes

### 🔧 6.2 API Testing & Documentation
**Goal**: Ensure API reliability and provide comprehensive documentation

#### ✅ Checklist:
- [ ] **CRITICAL**: Test API functionality locally
  - Run `uvicorn main:app --reload`
  - Test all endpoints with various parameters
  - Verify pagination works correctly
  - Test error scenarios (invalid IDs, empty results)
  - **VERIFY**: API behaves correctly in all scenarios

- [ ] **CRITICAL**: Verify automatic documentation
  - Access /docs endpoint for Swagger UI
  - Test all endpoints through interactive documentation
  - Ensure response models are correctly documented
  - **VERIFY**: Documentation is complete and functional

### 🔧 6.3 Production Deployment Strategy
**Goal**: Deploy API to free-tier hosting platform

#### ✅ Checklist:
- [ ] **CRITICAL**: Choose deployment platform (PythonAnywhere/Render)
  - Evaluate free tier limitations and requirements
  - Sign up for chosen platform
  - **VERIFY**: Platform meets project requirements

- [ ] **CRITICAL**: Deploy API to production
  - Upload code and requirements.txt
  - Configure environment variables (DATABASE_URL)
  - Set up web app configuration
  - Test deployment with live database
  - **VERIFY**: API is accessible and functional in production

- [ ] **CRITICAL**: Implement production monitoring
  - Set up basic logging and error tracking
  - Test API performance under load
  - Monitor database connection stability
  - **VERIFY**: Production system is stable and monitored

#### 🛑 Exit Criteria:
- FastAPI application provides all required endpoints
- API documentation is automatically generated and accessible
- Production deployment is stable and performs well
- All endpoints function correctly with live data

---

## 📊 PHASE 7: MONITORING & MAINTENANCE
**Milestone**: Robust System Health & Long-term Stability

### 🔧 7.1 Comprehensive Logging Implementation
**Goal**: Implement detailed logging for debugging and monitoring

#### ✅ Checklist:
- [ ] **CRITICAL**: Configure Scrapy logging
  ```python
  LOG_LEVEL = 'INFO'
  LOG_FILE = 'scrapy_log.txt'
  LOG_ENCODING = 'utf-8'
  LOG_STDOUT = True
  ```
  - **VERIFY**: Logs capture all scraping activity
  - **VERIFY**: Error conditions are properly logged

- [ ] **CRITICAL**: Implement FastAPI request logging
  - Configure uvicorn logging
  - Log API requests and responses
  - Track error rates and performance metrics
  - **VERIFY**: API activity is comprehensively logged

### 🔧 7.2 Automated Monitoring & Alerting
**Goal**: Proactive failure detection and notification

#### ✅ Checklist:
- [ ] **CRITICAL**: Implement workflow failure alerting
  - Configure email notifications for GitHub Actions failures
  - Set up MAIL_USERNAME and MAIL_PASSWORD secrets
  - Test alert system with intentional failures
  - **VERIFY**: Failure notifications are received promptly

- [ ] **CRITICAL**: Create data quality monitoring
  - Implement checks for data completeness
  - Monitor for unusual patterns or drops in data volume
  - Alert on potential scraper rot or site changes
  - **VERIFY**: Data quality issues are detected automatically

### 🔧 7.3 Maintenance Strategy Implementation
**Goal**: Prepare for long-term system sustainability

#### ✅ Checklist:
- [ ] **CRITICAL**: Document maintenance procedures
  - Create troubleshooting guide for common issues
  - Document CSS selector update procedures
  - Maintain list of target sites and their characteristics
  - **VERIFY**: Documentation is comprehensive and actionable

- [ ] **CRITICAL**: Implement resilient selector strategies
  - Use stable, semantic CSS selectors where possible
  - Implement fallback selectors for critical elements
  - Test selectors against site changes
  - **VERIFY**: Selectors are robust against minor site changes

- [ ] **CRITICAL**: Establish regular health checks
  - Schedule weekly log reviews
  - Monitor data volume trends
  - Check for new error patterns
  - **VERIFY**: Health check procedures are documented and schedulable

#### 🛑 Exit Criteria:
- Comprehensive logging captures all system activity
- Automated alerts notify of failures immediately
- Maintenance procedures are documented and tested
- System demonstrates resilience against common failure modes

---

## ⚖️ PHASE 8: LEGAL & ETHICAL COMPLIANCE
**Milestone**: Ensure Legal Operation & Ethical Standards

### 🔧 8.1 Legal Compliance Verification
**Goal**: Ensure all scraping activities comply with applicable laws

#### ✅ Checklist:
- [ ] **CRITICAL**: Verify CFAA compliance
  - Confirm all scraped data is publicly accessible
  - Ensure no login or paywall circumvention
  - Document public nature of all target content
  - **VERIFY**: Only public data is accessed

- [ ] **CRITICAL**: Review Terms of Service implications
  - Read ToS for all target websites
  - Document any explicit scraping prohibitions
  - Assess breach of contract risks
  - **VERIFY**: ToS compliance strategy is documented

- [ ] **CRITICAL**: Ensure copyright compliance
  - Limit extraction to facts (headlines, dates, URLs)
  - Avoid storing full article text
  - Implement proper attribution via source URLs
  - **VERIFY**: No copyrightable content is stored or redistributed

### 🔧 8.2 Ethical Guidelines Implementation
**Goal**: Implement responsible scraping practices

#### ✅ Checklist:
- [ ] **CRITICAL**: Implement comprehensive robots.txt compliance
  - Verify ROBOTSTXT_OBEY is enabled and working
  - Test compliance with various robots.txt configurations
  - Document compliance strategy
  - **VERIFY**: robots.txt directives are strictly followed

- [ ] **CRITICAL**: Ensure respectful resource usage
  - Monitor scraping impact on target servers
  - Implement conservative rate limiting
  - Use official APIs where available
  - **VERIFY**: Scraping behavior is respectful and sustainable

- [ ] **CRITICAL**: Implement data security measures
  - Secure database access with proper credentials
  - Protect sensitive configuration data
  - Implement appropriate access controls
  - **VERIFY**: Data is stored and accessed securely

#### 🛑 Exit Criteria:
- All scraping activities comply with applicable laws
- Ethical guidelines are implemented and documented
- System respects website resources and directives
- Data security best practices are followed

---

## 🎯 FINAL VALIDATION & LAUNCH
**Milestone**: Complete System Validation & Production Launch

### 🔧 Final Integration Testing
**Goal**: Validate entire system works as integrated whole

#### ✅ Pre-Launch Checklist:
- [ ] **CRITICAL**: End-to-end system test
  - Trigger GitHub Actions workflow manually
  - Verify RSS/sitemap discovery works
  - Confirm articles are scraped and stored
  - Test API returns fresh data
  - **VERIFY**: Complete data flow works flawlessly

- [ ] **CRITICAL**: Performance validation
  - Test system under various load conditions
  - Verify response times meet requirements
  - Confirm database performance is adequate
  - **VERIFY**: System meets performance expectations

- [ ] **CRITICAL**: Reliability verification
  - Run system for 24-48 hours continuously
  - Monitor for any failures or degradation
  - Verify error handling works correctly
  - **VERIFY**: System demonstrates production-ready reliability

- [ ] **CRITICAL**: Security audit
  - Verify no sensitive data is exposed
  - Confirm access controls are properly implemented
  - Test for potential security vulnerabilities
  - **VERIFY**: System meets security standards

### 🔧 Production Launch
**Goal**: Successfully deploy and monitor live system

#### ✅ Launch Checklist:
- [ ] **CRITICAL**: Enable production automation
  - Activate GitHub Actions schedule
  - Confirm API is live and accessible
  - Monitor initial automated runs
  - **VERIFY**: System operates automatically in production

- [ ] **CRITICAL**: Establish monitoring dashboard
  - Set up monitoring for key metrics
  - Configure alert thresholds
  - Test alert systems
  - **VERIFY**: Monitoring provides complete system visibility

- [ ] **CRITICAL**: Document operational procedures
  - Create runbook for common operations
  - Document troubleshooting procedures
  - Establish maintenance schedules
  - **VERIFY**: System is fully documented for ongoing operation

#### 🛑 Launch Success Criteria:
- System operates continuously without manual intervention
- All components work together seamlessly
- Data quality meets requirements
- Performance satisfies user needs
- Monitoring provides complete visibility
- Documentation enables effective maintenance

---

## 🎉 SUCCESS METRICS

### Key Performance Indicators (KPIs):
- **Uptime**: >99% system availability
- **Data Quality**: >95% successful article extraction rate
- **Deduplication**: 0% duplicate articles in database
- **Response Time**: API responses <500ms average
- **Cost**: $0 operational expenses (free-tier only)
- **Compliance**: 100% robots.txt compliance rate
- **Automation**: 0 manual interventions required per week

### Success Validation:
- [ ] System runs continuously for 30 days without intervention
- [ ] Database contains unique, high-quality news articles
- [ ] API provides fast, reliable access to data
- [ ] No legal or ethical violations detected
- [ ] All monitoring and alerting functions correctly
- [ ] System demonstrates scalability within free-tier limits

---

## 🚨 CRITICAL SUCCESS FACTORS

**NEVER PROCEED TO NEXT PHASE WITHOUT:**
1. ✅ All checkboxes completed in current phase
2. ✅ Exit criteria verified and documented
3. ✅ No blocking issues or failures detected
4. ✅ Performance meets minimum requirements
5. ✅ Security and compliance verified

**AI AGENT MUST:**
- Complete each checklist item before proceeding
- Verify all exit criteria before moving to next phase
- Document any deviations or issues encountered
- Test thoroughly at each milestone
- Maintain detailed logs of all activities
- Never skip verification steps for speed

**REMEMBER**: This system must work reliably in production. Thorough validation at each phase prevents costly failures later. Take time to do it right the first time.