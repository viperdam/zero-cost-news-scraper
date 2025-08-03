

### **Objective**

To construct a fully automated, zero-cost pipeline that continuously discovers and scrapes the latest news articles. The system will store the extracted data (highlights and publication time) in a central cloud database, implement an automatic deduplication mechanism to prevent repeat entries, and serve the unique news items through a simple API.

---

### **Phase 1: System Architecture & Data Persistence**

This phase establishes the foundational components for data storage and the core logic for preventing duplicates.

#### **1.1. Database Selection**

The system will use a **free-tier, cloud-hosted PostgreSQL database**.1 This choice provides a robust, remotely accessible, and professional-grade SQL database without incurring costs. It is ideal for storing structured data like news articles.1

* **Action:** Sign up for a free-tier PostgreSQL provider (e.g., Neon). You will receive a database connection URL, which will be used by both the scraper and the API.

#### **1.2. Database Schema and Deduplication Logic**

The core of the deduplication strategy lies within the database schema itself. A table named articles will be created with a specific rule to reject duplicates automatically.

* **Table Structure:**

| Column Name | Data Type | Constraints | Purpose |
| :---- | :---- | :---- | :---- |
| id | SERIAL | PRIMARY KEY | Unique identifier for each row. |
| url | TEXT | UNIQUE, NOT NULL | The URL of the article. The **UNIQUE** constraint is critical; the database will not allow two identical URLs to be inserted. |
| title | TEXT | NOT NULL | The headline or highlight of the article. |
| publication\_date | TIMESTAMP |  | The time the article was published. |
| summary | TEXT |  | A brief summary of the article. |

* **How Deduplication Works:** The UNIQUE constraint on the url column is the primary mechanism for preventing duplicates. When the scraper finds an article (new or old) and attempts to save it, the database will check if that URL already exists. If it does, the insertion will fail, thus automatically preventing the duplicate from being added.1 This directly addresses the requirement to compare against older news and not repeat entries.

---

### **Phase 2: The Scraping Engine with Integrated Deduplication**

This phase focuses on building the scraper using the Scrapy framework, which will handle data extraction and interact with the database pipeline.

#### **2.1. Scraper Development**

The core extraction logic will be built using **Scrapy**, a high-performance Python framework perfect for scalable scraping.3

* **Action:** Create a Scrapy project and a spider (news\_spider.py).6 This spider will be responsible for parsing the HTML of article pages to extract the title, publication date, and summary using CSS selectors.8

#### **2.2. The Database Pipeline**

Scrapy's "pipeline" feature will be used to process the scraped data and save it to the PostgreSQL database. This is where the deduplication logic is handled at the application level.

* **Action:** Implement a DatabasePipeline in the pipelines.py file.6 This pipeline will perform the following steps for each article the spider scrapes:  
  1. **Receive Scraped Item:** The pipeline receives the structured data (URL, title, etc.) from the spider.  
  2. **Attempt to Insert:** It connects to the PostgreSQL database and attempts to execute an INSERT command for the new article.  
  3. **Handle Duplicates Gracefully:** The code will be wrapped in a try...except block. If the INSERT command tries to add an article with a URL that already exists in the database, the UNIQUE constraint will cause the database to raise an IntegrityError. The pipeline will catch this specific error, log that a duplicate was found, and simply move on to the next item without crashing. This ensures the scraper continues its work even when it re-discovers old articles.

---

### **Phase 3: Continuous Operation & Automation**

To ensure the system continuously scrapes for new content, the entire process will be automated and scheduled to run at regular intervals.

#### **3.1. Discovering New Articles**

Instead of crawling entire websites, the scraper will first fetch new article URLs from publisher-provided **RSS feeds and XML sitemaps**.9 This is a highly efficient and respectful method for discovering the latest content.11

#### **3.2. Automated Scheduling**

The scraping process will be scheduled using **GitHub Actions**, a free and powerful automation tool.

* **Action:** Create a workflow file (.github/workflows/scrape.yml) in your project's repository.  
* **Configuration:**  
  * **Schedule:** Configure the workflow to run on a schedule using cron syntax (e.g., '0 \* \* \* \*' to run at the top of every hour).12  
  * **Execution:** The workflow will automatically check out the code, install dependencies, and run the Scrapy spider.  
  * **Security:** The database connection URL will be stored securely as a GitHub Secret and passed to the scraper at runtime.

---

### **Phase 4: Data Delivery via API**

The final step is to make the collected and deduplicated news available.

* **Action:** A lightweight API will be built using the **FastAPI** framework. This API will connect to the same PostgreSQL database, read the stored articles, and provide simple endpoints for users to retrieve the news data.  
* **Hosting:** The API will be deployed on a free-tier Platform-as-a-Service (PaaS) like PythonAnywhere or Render, which provides an always-on environment to serve requests.

### **Final Workflow Summary**

1. **Scheduled Trigger:** The GitHub Actions workflow starts automatically on the defined schedule (e.g., hourly).  
2. **Discovery:** The system first checks RSS feeds of target news sites to get a list of the latest article URLs.  
3. **Scraping:** The Scrapy spider visits each new URL and extracts the required data (title, publication date).  
4. **Deduplication & Storage:** For each article, the Scrapy pipeline attempts to insert it into the PostgreSQL database. The database's UNIQUE constraint on the URL automatically rejects any duplicates.  
5. **Continuous Loop:** The process repeats at the next scheduled interval, ensuring the database is always updated with the latest, unique news.  
6. **API Access:** The live FastAPI application continuously serves the clean, deduplicated data from the database on demand.

This plan provides a complete, resilient, and cost-free solution for continuous news aggregation with built-in deduplication.

#### **Geciteerd werk**

1. Data Storage for Web Scraping: A Comprehensive Guide \- Scrapeless, geopend op augustus 2, 2025, [https://www.scrapeless.com/en/blog/data-storage](https://www.scrapeless.com/en/blog/data-storage)  
2. Web scraping: How do I store data? : r/AskProgramming \- Reddit, geopend op augustus 2, 2025, [https://www.reddit.com/r/AskProgramming/comments/s09ag6/web\_scraping\_how\_do\_i\_store\_data/](https://www.reddit.com/r/AskProgramming/comments/s09ag6/web_scraping_how_do_i_store_data/)  
3. Web Scraping With Scrapy: The Complete Guide in 2025 \- Scrapfly, geopend op augustus 2, 2025, [https://scrapfly.io/blog/posts/web-scraping-with-scrapy](https://scrapfly.io/blog/posts/web-scraping-with-scrapy)  
4. How to create Scalable Web Scraping Pipelines Using Python and Scrapy, geopend op augustus 2, 2025, [https://www.vocso.com/blog/how-to-create-scalable-web-scraping-pipelines-using-python-and-scrapy/](https://www.vocso.com/blog/how-to-create-scalable-web-scraping-pipelines-using-python-and-scrapy/)  
5. Scrapy, geopend op augustus 2, 2025, [https://www.scrapy.org/](https://www.scrapy.org/)  
6. Web Scraping with Scrapy: Python Tutorial \- Oxylabs, geopend op augustus 2, 2025, [https://oxylabs.io/blog/scrapy-web-scraping-tutorial](https://oxylabs.io/blog/scrapy-web-scraping-tutorial)  
7. Scrapy Tutorial — Scrapy 2.13.3 documentation, geopend op augustus 2, 2025, [https://docs.scrapy.org/en/latest/intro/tutorial.html](https://docs.scrapy.org/en/latest/intro/tutorial.html)  
8. Implementing Web Scraping in Python with Scrapy \- GeeksforGeeks, geopend op augustus 2, 2025, [https://www.geeksforgeeks.org/python/implementing-web-scraping-python-scrapy/](https://www.geeksforgeeks.org/python/implementing-web-scraping-python-scrapy/)  
9. Best practices for XML sitemaps and RSS/Atom feeds | Google Search Central Blog, geopend op augustus 2, 2025, [https://developers.google.com/search/blog/2014/10/best-practices-for-xml-sitemaps-rssatom](https://developers.google.com/search/blog/2014/10/best-practices-for-xml-sitemaps-rssatom)  
10. Fundus: A Simple-to-Use News Scraper Optimized for High Quality Extractions \- arXiv, geopend op augustus 2, 2025, [https://arxiv.org/html/2403.15279v1](https://arxiv.org/html/2403.15279v1)  
11. \#1 WordPress RSS Feed & Footer Plugin \- All in One SEO \- AIOSEO, geopend op augustus 2, 2025, [https://aioseo.com/features/rss-content/](https://aioseo.com/features/rss-content/)  
12. Webscraper that scrapes every hour : r/datascience \- Reddit, geopend op augustus 2, 2025, [https://www.reddit.com/r/datascience/comments/tuwbi1/webscraper\_that\_scrapes\_every\_hour/](https://www.reddit.com/r/datascience/comments/tuwbi1/webscraper_that_scrapes_every_hour/)