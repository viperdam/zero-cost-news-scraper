

# **A Comprehensive Guide to Building a Zero-Cost, Continuous News Scraping Pipeline**

## **Part I: Architectural Blueprint for a Zero-Cost News Aggregation System**

The development of a robust, automated news scraping system presents a significant engineering challenge, particularly when constrained by a strict zero-cost requirement. This constraint fundamentally shapes the project's architecture, necessitating a strategic shift away from resource-intensive commercial tools and toward a highly optimized, efficiency-driven design. This report provides a comprehensive, start-to-finish blueprint for constructing such a system, covering technology selection, implementation, deployment, and long-term maintenance. The architecture is designed for stability, continuous operation, and resilience against common anti-scraping measures, all while adhering to the zero-cost principle.

### **System Overview: The Data Flow Pipeline**

The proposed system is architected as a four-stage data pipeline, ensuring a logical and modular flow from data discovery to final delivery. Each stage is handled by a distinct component chosen specifically for its performance and robust free-tier availability.

1. **Discovery:** This initial stage focuses on efficiently identifying the URLs of new articles without resorting to brute-force crawling of entire websites. The system will primarily leverage publisher-provided RSS/Atom feeds and XML sitemaps, which are structured, machine-readable files intended for content syndication and search engine indexing.1 This approach is significantly more efficient and less likely to trigger anti-bot defenses than traditional web crawling.  
2. **Extraction:** Once a list of target URLs is compiled, the core scraping engine takes over. This stage involves fetching the HTML content of each article page and extracting the required data points: the headline (highlight), the publication time, and a brief summary. The Python-based Scrapy framework is selected for this task due to its high-performance asynchronous architecture, which is critical for maximizing efficiency in resource-constrained environments.3  
3. **Persistence:** The structured data extracted by the scraper must be stored in a durable, queryable format. Instead of relying on simple flat files (like CSV or JSON), which are difficult to manage and scale, the system will use a free-tier, cloud-hosted relational database. This provides the benefits of a professional-grade database—such as data integrity, indexing, and remote accessibility—without incurring costs.5  
4. **Delivery:** The final stage makes the collected data available to end-users or other applications. A lightweight, high-performance API will be built to serve the data from the cloud database. This API will provide endpoints for retrieving the latest news, searching for specific articles, and paginating through results, all delivered in a standard JSON format.

This modular pipeline ensures that each component can be developed, tested, and maintained independently, contributing to the overall stability and scalability of the system.

### **The Zero-Cost Technology Stack: A Strategic Selection**

The selection of each technology in the stack is a deliberate choice driven by the zero-cost mandate. This is not merely about finding free tools, but about selecting components whose free tiers are generous and stable enough to support a continuous, production-level workload. The architecture is an exercise in maximizing the value of free resources through intelligent engineering rather than solving problems with financial expenditure, a common approach in the commercial scraping industry that relies on paid APIs and vast proxy networks.6

The chosen technology stack is as follows:

* **Core Language:** Python 3.8+  
* **Discovery Engine:** Python libraries feedparser and ultimate-sitemap-parser.  
* **Extraction Engine:** Scrapy, a powerful and fast open-source web scraping framework.9  
* **Data Persistence:** A free-tier cloud PostgreSQL database, with Neon being the recommended provider due to its generous allowances and modern serverless architecture.11  
* **API Framework:** FastAPI, a modern Python framework known for its high performance and automatic, interactive API documentation.13  
* **Deployment & Scheduling:** GitHub Actions for scheduling and executing the scraper, and a free-tier Platform-as-a-Service (PaaS) like PythonAnywhere or Render for continuously hosting the API.

The following table provides a detailed justification for these choices by comparing them against viable free alternatives.

**Table 1: Zero-Cost Technology Stack Comparison**

| Component | Recommended Choice | Rationale | Free Alternative(s) | Why Alternative Was Not Chosen |
| :---- | :---- | :---- | :---- | :---- |
| **Scraping Engine** | Scrapy | High-performance asynchronous architecture maximizes throughput on resource-limited free tiers. Full-featured framework with built-in support for middlewares and data pipelines.4 | Requests \+ BeautifulSoup | Synchronous nature leads to inefficient use of limited CPU time (spent waiting for I/O). Requires manual implementation of features like retries, scheduling, and data pipelines.15 |
| **Database** | Free-Tier Cloud PostgreSQL (Neon) | Provides a managed, remotely accessible, and scalable SQL database. Neon's free tier is generous and its serverless nature is cost-effective. Ensures data integrity and allows for complex queries.5 | SQLite | File-based nature complicates concurrent access between the scraper and a remotely hosted API. Less scalable for larger datasets.17 |
|  |  |  | Free-Tier MongoDB Atlas | NoSQL flexibility is beneficial but can be less structured. Free tier is slightly less generous in some aspects. PostgreSQL is a more traditional and robust choice for structured news data.19 |
| **API Framework** | FastAPI | Extremely high performance, automatic data validation with Pydantic, and self-generating interactive documentation (Swagger UI). Modern and developer-friendly.13 | Flask | A solid and mature framework, but slower than FastAPI out-of-the-box and requires additional libraries for data validation and API documentation, adding complexity.22 |
| **Deployment/Scheduler** | GitHub Actions \+ PythonAnywhere/Render | GitHub Actions provides a robust, free, and serverless environment for scheduled tasks (cron jobs).24 PythonAnywhere offers a persistent, always-on free tier for hosting the web API, despite its limitations.25 | Local Cron Job | Requires a dedicated, always-on local machine, which is not a reliable or scalable solution. Fails if the machine is turned off or loses internet connection.27 |
|  |  |  | AWS Free Tier (EC2/Lambda) | The free tier is often temporary (12 months) and has complex usage limits that can easily lead to unexpected costs. Requires more complex setup and management. |

---

## **Part II: Efficient News Discovery: Leveraging RSS Feeds and Sitemaps**

A core principle of sustainable and polite web scraping is to utilize the structured data pathways that website publishers intentionally provide. For news websites, whose business model relies on the dissemination and discovery of their content, these pathways most often take the form of RSS feeds and XML sitemaps. Bypassing these purpose-built tools in favor of brute-force crawling is not only inefficient and resource-intensive but also a primary trigger for anti-scraping mechanisms.

### **The Rationale for a Targeted Approach**

News organizations want their articles to be found, indexed by search engines, and read by aggregators. To facilitate this, they adhere to web standards that provide machine-readable lists of their content. The two most important formats are XML Sitemaps and RSS/Atom feeds.1

* **XML Sitemaps:** These are typically large files designed for search engines. They provide a comprehensive list of all canonical URLs on a site, often with metadata like the last modification date. Their purpose is to ensure complete site indexing.29  
* **RSS/Atom Feeds:** These are smaller, more dynamic files that list only the most recent updates to a site. They are designed for news aggregators and readers who need to know about new content as soon as it is published.31

For optimal crawling, a hybrid strategy is recommended. The system should first parse the XML sitemap to build a complete historical database of articles and then periodically poll the RSS/Atom feed to discover new articles in near real-time. This two-pronged approach ensures both comprehensive coverage and timely updates.1

Adopting this discovery method is, in itself, a powerful anti-blocking technique. Anti-bot systems are designed to detect anomalous, aggressive behavior. A scraper that attempts to crawl every link on a news homepage generates a high volume of requests in an unpredictable pattern, a clear signature of an unsolicited bot. In contrast, a scraper that makes a single, periodic request to a well-known endpoint like /rss.xml or /sitemap.xml behaves identically to legitimate services like Google News, Feedly, or other news aggregators. By mimicking this legitimate traffic pattern, the scraper avoids raising initial red flags, making the entire system more resilient and reducing the burden on other evasion tactics.

### **Implementation: Finding and Parsing Feeds**

The first step in the discovery process is to locate the relevant feed URLs for each target news source.

#### **Finding Feed URLs**

There are several reliable methods to find a website's RSS feed or sitemap:

1. **Check Common Locations:** The most straightforward method is to try common URL patterns. Append suffixes like /sitemap.xml, /sitemap\_index.xml, /rss.xml, /feed, or /rss to the website's root domain.32  
2. **Inspect the robots.txt File:** Many websites explicitly declare the location of their sitemap in their robots.txt file (accessible at https://www.websitedomain.com/robots.txt). Look for a line that starts with Sitemap:.29  
3. **View Page Source:** The RSS feed URL is often linked in the \<head\> section of a website's HTML. Right-click on the homepage, select "View Page Source," and search (Ctrl+F or Cmd+F) for "rss" or "atom". The URL will typically be in a \<link\> tag with type="application/rss+xml".32  
4. **Use Browser Extensions:** Extensions like "RSS Feed URL Finder" can automatically detect and display the feed URLs for the current page.35

#### **Parsing RSS Feeds with feedparser**

Once an RSS feed URL is identified, the feedparser library provides a simple and robust way to parse its contents. It normalizes various feed formats (RSS, Atom, RDF) into a consistent Python dictionary structure.36

First, install the library:

Bash

pip install feedparser

The following Python script demonstrates how to parse a feed and extract the title, link, and publication date for each entry.

Python

import feedparser

def parse\_rss\_feed(feed\_url: str):  
    """  
    Parses an RSS feed and extracts details for each entry.

    Args:  
        feed\_url: The URL of the RSS feed.  
    """  
    \# The parse() function fetches and parses the feed  
    blog\_feed \= feedparser.parse(feed\_url)

    \# The 'bozo' key is set to 1 if the feed is malformed  
    if blog\_feed.bozo:  
        print(f"Error parsing feed: {blog\_feed.bozo\_exception}")  
        return

    print(f"--- Blog: {blog\_feed.feed.title} \---")  
    print(f"--- Link: {blog\_feed.feed.link} \---\\n")

    \# The 'entries' key contains a list of all posts  
    for entry in blog\_feed.entries:  
        print(f"Title: {entry.title}")  
        print(f"Link: {entry.link}")  
        \# Publication date is in a structured time format  
        if 'published\_parsed' in entry:  
            print(f"Published: {entry.published\_parsed}")  
        elif 'updated\_parsed' in entry:  
            print(f"Updated: {entry.updated\_parsed}")  
        print("-" \* 20)

\# Example usage with a sample RSS feed URL  
\# Replace with the actual feed URL of the target news site  
rss\_url \= "https://www.geeksforgeeks.org/feed/"  
parse\_rss\_feed(rss\_url)

This script effectively extracts the necessary article URLs and their publication times, which can then be passed to the Scrapy scraper for content extraction.38

#### **Parsing Sitemaps with ultimate-sitemap-parser**

For comprehensive URL discovery, the ultimate-sitemap-parser library is an excellent choice. It is specifically designed to handle complex sitemap structures, including nested index sitemaps, and is highly performant.40

First, install the library:

Bash

pip install ultimate-sitemap-parser

The following script shows how to use the library to fetch all URLs from a website's sitemap, starting from its homepage.

Python

from usp.tree import sitemap\_tree\_for\_homepage

def get\_all\_urls\_from\_sitemap(homepage\_url: str):  
    """  
    Fetches and parses a website's sitemap to extract all URLs.

    Args:  
        homepage\_url: The homepage URL of the target website.  
    """  
    try:  
        \# This function automatically finds, fetches, and parses the sitemap(s)  
        tree \= sitemap\_tree\_for\_homepage(homepage\_url)

        \# The.all\_pages() method returns a generator for all URLs found  
        print(f"--- Found URLs for {homepage\_url} \---")  
        url\_count \= 0  
        for page in tree.all\_pages():  
            print(page.url)  
            url\_count \+= 1  
        print(f"\\n--- Total URLs found: {url\_count} \---")

    except Exception as e:  
        print(f"An error occurred: {e}")

\# Example usage with a sample homepage URL  
\# Replace with the actual homepage of the target news site  
target\_site \= "https://www.asos.com/"  
get\_all\_urls\_from\_sitemap(target\_site)

This simple yet powerful script abstracts away the complexity of parsing XML and handling nested sitemaps, providing a clean list of all discoverable article URLs on the site.41

---

## **Part III: Core Scraper Implementation with Scrapy**

With a reliable method for discovering article URLs, the next step is to build the core extraction engine. Scrapy is the ideal framework for this task. Its asynchronous, event-driven architecture allows it to handle a large volume of requests concurrently, making it exceptionally fast and memory-efficient.3 This high performance is not merely a convenience; it is a critical feature that enables the scraper to operate effectively within the stringent resource limits of free-tier hosting platforms. A synchronous scraper using a library like

requests would spend the majority of its limited CPU allocation idly waiting for network responses. Scrapy, by contrast, utilizes this idle time to process other requests, maximizing throughput and ensuring the system can scale without incurring costs.4

### **Setting Up a Scrapy Project**

To begin, install Scrapy using pip:

Bash

pip install scrapy

Next, create a new Scrapy project. Navigate to your desired directory in the terminal and run:

Bash

scrapy startproject news\_scraper

This command creates a new directory named news\_scraper with the following structure 42:

news\_scraper/  
├── scrapy.cfg            \# deploy configuration file  
└── news\_scraper/  
    ├── \_\_init\_\_.py  
    ├── items.py          \# project items definition file  
    ├── middlewares.py    \# project middlewares file  
    ├── pipelines.py      \# project pipelines file  
    ├── settings.py       \# project settings file  
    └── spiders/  
        ├── \_\_init\_\_.py  
        \# Spiders will be placed here

* **spiders/**: This directory will contain the Python files for each spider you create.  
* **items.py**: Defines the data structure (schema) for the items you plan to scrape.  
* **pipelines.py**: Processes the scraped items, for example, by cleaning data or saving it to a database.  
* **settings.py**: Contains all the configuration settings for the project, such as enabling middlewares, setting request delays, and configuring pipelines.

### **Developing the Spider**

A "spider" is a class that defines how a specific site (or group of sites) will be scraped, including how to perform the crawl and how to extract data from its pages.42 To create a spider, generate a new Python file inside the

news\_scraper/spiders/ directory, for example, news\_spider.py.

The following code provides a basic structure for a news article spider. It is designed to receive a list of URLs (discovered in Part II) and process each one.

Python

\# In news\_scraper/spiders/news\_spider.py  
import scrapy  
from news\_scraper.items import NewsArticleItem

class NewsSpider(scrapy.Spider):  
    \# A unique name for the spider  
    name \= 'news\_spider'

    def \_\_init\_\_(self, urls=None, \*args, \*\*kwargs):  
        super(NewsSpider, self).\_\_init\_\_(\*args, \*\*kwargs)  
        \# The list of URLs is passed in when the spider is run  
        self.start\_urls \= urls.split(',') if urls else

    def parse(self, response):  
        """  
        This method is called for each response downloaded.  
        It's responsible for parsing the response and extracting scraped data.  
        """  
        \# Instantiate the item  
        article \= NewsArticleItem()

        \# Extract data using CSS Selectors (examples)  
        article\['url'\] \= response.url  
        article\['title'\] \= response.css('h1.article-title::text').get()  
        article\['publication\_date'\] \= response.css('span.publication-date::text').get()  
          
        \# Example of extracting a summary from the first two paragraph tags  
        summary\_paragraphs \= response.css('div.article-body p::text').getall()  
        article\['summary'\] \= ' '.join(summary\_paragraphs\[:2\])

        \# Yield the populated item to be processed by pipelines  
        yield article

This spider defines three key components:

* **name**: A unique identifier for the spider, used when running a crawl (scrapy crawl news\_spider).  
* **\_\_init\_\_**: The constructor allows a comma-separated string of URLs to be passed to the spider from the command line, which populates the start\_urls attribute.  
* **parse()**: This is the default callback method in Scrapy. It is executed for every URL in start\_urls. The response object contains the page's content and provides powerful methods for data extraction.43

### **Data Extraction with Selectors**

Scrapy has built-in support for extracting data using CSS and XPath selectors. CSS selectors are often more readable and are sufficient for most news scraping tasks.44

To find the correct selectors, use your browser's developer tools:

1. Navigate to a target news article page.  
2. Right-click on the element you want to extract (e.g., the main headline).  
3. Select "Inspect" from the context menu.  
4. The developer tools will open, highlighting the HTML element in the source code.  
5. Identify a unique class, ID, or tag structure that can be used to target the element. For example, a headline might be inside an \<h1\> tag with a class of article-title.

The spider code uses response.css() to apply these selectors:

* response.css('h1.article-title::text').get(): This selects the text content (::text) of the first \<h1\> element with the class article-title. The .get() method returns the first matching element as a string, or None if no element is found.  
* response.css('div.article-body p::text').getall(): This selects the text content of all \<p\> tags inside a \<div\> with the class article-body. The .getall() method returns a list of all matching strings.

### **Structuring Data with Items**

To ensure data consistency, it's a best practice to use Scrapy Items. An Item is a simple container for scraped data, similar to a Python dictionary, but it provides a fixed structure that helps prevent typos and ensures all required fields are populated.42

Define the NewsArticleItem in the news\_scraper/items.py file:

Python

\# In news\_scraper/items.py  
import scrapy

class NewsArticleItem(scrapy.Item):  
    \# define the fields for your item here like:  
    url \= scrapy.Field()  
    title \= scrapy.Field()  
    publication\_date \= scrapy.Field()  
    summary \= scrapy.Field()

By instantiating this item in the spider (article \= NewsArticleItem()) and populating its fields, the data is passed through the Scrapy engine in a predictable, structured format, ready for processing by the database pipeline.

---

## **Part IV: Evasion and Politeness: Strategies for Sustainable, Uninterrupted Scraping**

A crucial requirement for a continuous scraping system is its ability to operate without being detected and blocked. For a zero-cost project, this cannot be achieved through expensive solutions like large-scale residential proxy networks.45 Instead, the strategy must pivot to one of "politeness" and sophisticated evasion—making the scraper behave less like an aggressive bot and more like a considerate, human-like user. This section details the free but highly effective techniques to build a resilient and respectful scraper.

### **Foundational Principles: The "Good Bot" Ethos**

The first line of defense is to adhere to the established rules of the web and to be mindful of the target server's resources.

#### **Respecting robots.txt**

The Robots Exclusion Protocol, or robots.txt, is a standard used by websites to communicate with web crawlers and other automated bots. This simple text file, located at the root of a domain, specifies which parts of the site should not be accessed by bots.47 Scrapy is designed to be a "good bot" and respects these rules by default. The

ROBOTSTXT\_OBEY setting in settings.py is set to True in new projects. It is critical to leave this setting enabled to ensure compliance and avoid being blocked for violating explicit directives.48

#### **Rate Limiting and Politeness with AutoThrottle**

Sending requests too quickly is the most common reason scrapers get banned. A high request rate can overload a website's server, and anti-bot systems are designed to detect and block IP addresses that exhibit such aggressive behavior.47 Scrapy's

AutoThrottle extension is an essential tool for managing this. It dynamically adjusts the scraping speed based on the load it's imposing on both the scraper's machine and the target website's server.

To enable and configure AutoThrottle, add the following to settings.py:

Python

\# In news\_scraper/settings.py

\# Enable the AutoThrottle extension  
AUTOTHROTTLE\_ENABLED \= True  
\# The initial download delay (in seconds)  
AUTOTHROTTLE\_START\_DELAY \= 5  
\# The maximum download delay to be set in case of high latencies  
AUTOTHROTTLE\_MAX\_DELAY \= 60  
\# The average number of requests Scrapy should be sending in parallel to each remote server  
AUTOTHROTTLE\_TARGET\_CONCURRENCY \= 1.0  
\# Enable showing throttling stats for every response received:  
AUTOTHROTTLE\_DEBUG \= False

This configuration instructs Scrapy to start with a 5-second delay between requests, aim for only one concurrent request to any given server, and adjust the delay (up to 60 seconds) if the server starts responding slowly.3 This mimics a more patient, human-like browsing pattern and significantly reduces the risk of being flagged for aggressive crawling.

### **Advanced Evasion at Zero Cost**

Beyond basic politeness, a scraper must also disguise its identity to avoid being filtered by more sophisticated anti-bot systems.

#### **User-Agent and Header Rotation**

When a browser makes a request, it sends a collection of HTTP headers, including the User-Agent string, which identifies the browser, its version, and the operating system.49 Default User-Agents from libraries like Python's

requests or Scrapy immediately identify the traffic as automated, making it an easy target for blocking.51

To appear as a legitimate user, the scraper must send realistic browser headers and rotate them frequently. This can be implemented using a Scrapy Downloader Middleware.

1. **Create a Middleware File:** Create a file custom\_middlewares.py in the news\_scraper directory.  
2. **Implement the Middleware:** The following code defines a middleware that randomly selects a User-Agent from a list and sets other realistic browser headers for each request.

Python

\# In news\_scraper/custom\_middlewares.py  
import random

class RotateUserAgentMiddleware:  
    \# A list of real-world User-Agent strings  
    USER\_AGENTS \=

    def process\_request(self, request, spider):  
        \# Randomly select a User-Agent for the request  
        user\_agent \= random.choice(self.USER\_AGENTS)  
        request.headers\['User-Agent'\] \= user\_agent

        \# Set other realistic browser headers  
        request.headers.setdefault('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,\*/\*;q=0.8')  
        request.headers.setdefault('Accept-Language', 'en-US,en;q=0.9')  
        request.headers.setdefault('Accept-Encoding', 'gzip, deflate, br')  
        request.headers.setdefault('Connection', 'keep-alive')  
        request.headers.setdefault('Upgrade-Insecure-Requests', '1')  
        request.headers.setdefault('Sec-Fetch-Dest', 'document')  
        request.headers.setdefault('Sec-Fetch-Mode', 'navigate')  
        request.headers.setdefault('Sec-Fetch-Site', 'none')  
        request.headers.setdefault('Sec-Fetch-User', '?1')

3. **Enable the Middleware:** In settings.py, add the middleware to the DOWNLOADER\_MIDDLEWARES dictionary. The number indicates the order of execution.

Python

\# In news\_scraper/settings.py  
DOWNLOADER\_MIDDLEWARES \= {  
   'news\_scraper.custom\_middlewares.RotateUserAgentMiddleware': 543,  
}

This ensures that every request sent by Scrapy will have a different, realistic browser identity, making it much harder to profile and block the scraper based on its headers.51 It is crucial that the other headers are consistent with the chosen User-Agent; for example, do not send Firefox-specific headers with a Chrome User-Agent.51

#### **Handling Dynamic Content via API Reverse-Engineering**

Modern news sites often use JavaScript to load content dynamically after the initial page load. While browser automation tools like Selenium or Playwright can render this content, they are extremely resource-intensive (CPU, memory) and slow, making them unsuitable for a zero-cost, high-volume system.53

A far more efficient, zero-cost method is to reverse-engineer the website's internal API calls.56 When a browser loads dynamic content, it typically makes background requests (often called XHR or Fetch requests) to an API endpoint, which returns the data in a structured format like JSON. By identifying and replicating these requests, the scraper can get the raw data directly, bypassing the need for browser rendering entirely.

The process is as follows:

1. **Open Browser Developer Tools:** Navigate to the target page and open the developer tools (F12 or right-click and "Inspect").  
2. **Monitor Network Traffic:** Go to the "Network" tab and filter for "Fetch/XHR" requests.  
3. **Trigger the Dynamic Content:** Perform the action that loads the content (e.g., scroll down, click a "Load More" button).  
4. **Identify the API Request:** Observe the new requests that appear in the Network tab. Look for one that returns the desired data, often in JSON format.  
5. **Replicate the Request in Scrapy:** Analyze the request's URL, method (GET/POST), headers, and any payload. Then, construct an identical scrapy.Request or scrapy.FormRequest in your spider to fetch this data directly.58

This technique is significantly faster and uses a fraction of the resources compared to a headless browser, making it the superior choice for handling dynamic content within a zero-cost framework.

#### **The Proxy Dilemma: Why Free Proxies Are Not a Solution**

While rotating IP addresses is a common anti-blocking strategy, using free proxies is highly discouraged for a stable, continuous system. Free proxy lists are notoriously unreliable; the IPs are often slow, quickly blacklisted, and can even be malicious, potentially compromising your data. For a system that needs to run autonomously, the high failure rate of free proxies would lead to constant errors and incomplete data. While paid residential proxies are highly effective, they are expensive and fall outside the project's scope.60 Therefore, the recommended strategy is to focus on making the scraper's behavior from its single, static IP address as impeccable as possible through the politeness and evasion techniques described above.

### **Evading Fingerprinting and CAPTCHAs**

Advanced anti-bot systems employ more sophisticated detection methods that must be understood and mitigated.

#### **Browser Fingerprinting**

Websites can identify and track users (and bots) by creating a "fingerprint" from a combination of browser and system characteristics, such as installed fonts, screen resolution, browser plugins, and specific rendering outputs from Canvas and WebGL APIs.61 Headless browsers are particularly vulnerable to fingerprinting, as they often have unique properties (like reporting

navigator.webdriver as true) that expose them as automated tools.63 The most effective zero-cost defense against fingerprinting is to avoid using headless browsers altogether and rely on direct HTTP requests and API reverse-engineering.

#### **CAPTCHA Handling**

A CAPTCHA (Completely Automated Public Turing test to tell Computers and Humans Apart) is a challenge designed to block bots. Encountering a CAPTCHA is a definitive sign that the scraper's activity has been detected as aggressive or non-human.64 While there are paid services that can solve CAPTCHAs programmatically, they are not an option for this project.65 The only zero-cost solution is prevention. By strictly adhering to the politeness principles—respecting

robots.txt, using AutoThrottle for slow and randomized request rates, and rotating realistic headers—the scraper can avoid triggering the thresholds that lead to CAPTCHA challenges in the first place.

**Table 2: Anti-Blocking Techniques: Cost vs. Efficacy**

| Technique | Efficacy | Implementation Complexity | Cost | Recommendation for this Project |
| :---- | :---- | :---- | :---- | :---- |
| **Rate Limiting (AutoThrottle)** | High | Low | Free | **Essential**. The primary method for politeness and ban avoidance. |
| **User-Agent/Header Rotation** | High | Medium | Free | **Essential**. A core requirement for masking the scraper's identity. |
| **API Reverse-Engineering** | Very High | High | Free | **Highly Recommended** for dynamic content. Superior to headless browsers. |
| **Headless Browsers (Selenium)** | Medium | High | Free (High CPU/RAM cost) | **Avoid**. Too resource-intensive for free tiers and easily fingerprinted. |
| **Free Proxies** | Very Low | Medium | Free | **Do Not Use**. Unreliable, slow, and insecure. Will compromise system stability. |
| **Paid Datacenter Proxies** | Medium | Low | Paid | Not Recommended. Outside the zero-cost constraint and easily detectable.66 |
| **Paid Residential Proxies** | Very High | Low | Paid | Not Recommended. The most effective solution, but far outside the zero-cost constraint.60 |
| **CAPTCHA Solving Services** | High | Medium | Paid | Not Recommended. Outside the zero-cost constraint. Focus on prevention. |

---

## **Part V: Data Persistence: Selecting and Implementing a Free-Tier Database**

Once data is scraped, it must be stored in a way that is durable, scalable, and accessible to the API. While writing to a simple CSV or JSON file is easy, it is not a viable long-term solution for a continuous system. Such files are prone to corruption, are inefficient to query, and do not handle concurrent access well.67 A proper database is essential for the system's stability and functionality.

### **Analysis of Zero-Cost Storage Options**

Several database options are available that can be implemented at no cost:

* **SQLite:** This is a serverless, self-contained, file-based SQL database engine. It is built into Python via the sqlite3 module, making it incredibly easy to set up for local development and testing.17 However, its file-based nature presents challenges for a deployed application where the scraper (running on GitHub Actions) and the API (running on a separate platform like PythonAnywhere) need to access the same database file. While possible to sync the file, it adds significant complexity and is not a robust solution for concurrent operations.  
* **Free-Tier Cloud Databases:** This is the recommended approach. A cloud database is a managed service that runs on a remote server, accessible over the internet. This model perfectly suits the distributed nature of the system, allowing both the scraper and the API to connect to a central data store from different locations. Several providers offer "forever free" tiers that are suitable for small-to-medium scale projects.

### **Deep Dive: Free-Tier Cloud PostgreSQL and MongoDB**

The two most popular choices for free-tier cloud databases are PostgreSQL (a relational/SQL database) and MongoDB (a non-relational/NoSQL database).

* **MongoDB Atlas:** The M0 "Shared" tier offers 512 MB of storage and shared CPU/RAM. MongoDB's flexible, document-based (JSON-like) data model is often well-suited for scraped data, which can sometimes have a variable structure.19  
* **Neon (PostgreSQL):** Neon's free tier is particularly generous, offering 0.5 GB of storage, 10 projects, and a significant allocation of compute hours.11 As a relational database, PostgreSQL enforces a strict schema, which is beneficial for news articles that have a consistent structure (title, date, summary), ensuring data integrity.

The recent shutdown of ElephantSQL, another popular free PostgreSQL provider, serves as a critical lesson in the potential volatility of the free-tier market.69 This highlights a significant risk: building a system that is tightly coupled to a single provider can lead to a major crisis if that service is discontinued.

This risk underscores the importance of architectural resilience. The most effective way to mitigate this is to design the application to be database-agnostic by using an Object-Relational Mapper (ORM). An ORM, such as SQLAlchemy, acts as a translation layer between the Python application code and the database. The application interacts with high-level Python objects, and the ORM handles the conversion of these interactions into the specific SQL dialect of the underlying database. If the database provider needs to be changed (e.g., migrating from Neon to another PostgreSQL service, or even to a different SQL database entirely), only the database connection string in the configuration needs to be updated. The core application logic remains untouched. This architectural decision to use an ORM is a direct response to the inherent risks of relying on free-tier services, ensuring the system's long-term stability and maintainability.

**Table 3: Free-Tier Cloud Database Analysis**

| Provider | Database Type | Storage Limit | Compute/RAM Limit | Connection Limit | Key Features | Longevity/Risk Assessment |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **Neon** | PostgreSQL | 0.5 GB | 190 compute hrs/mo, Autoscaling | Not explicitly limited on free tier | Serverless architecture, branching, generous compute allowance. | High. Well-funded, modern platform. Low immediate risk. |
| **MongoDB Atlas** | NoSQL (Document) | 512 MB | Shared vCPU/RAM | 500 | Flexible schema, widely used in modern web dev. | High. Backed by MongoDB, Inc. Very low risk. |
| **Supabase** | PostgreSQL | 500 MB | Shared, 1 CPU Core | 60 | Integrated auth, storage, and auto-generated APIs. | Medium-High. Popular open-source alternative to Firebase. |
| **ElephantSQL** | PostgreSQL | 20 MB | N/A | 5 | Simple, was a popular choice for hobbyists. | **Discontinued**. Service shutting down Jan 2025\.70 Serves as a cautionary tale. |

Given its generous limits and the robustness of PostgreSQL for structured data, **Neon** is the recommended choice for this project.

### **Implementation: Integrating Scrapy with the Database**

To save scraped data to the database, a Scrapy Item Pipeline is used. This pipeline receives the structured NewsArticleItem from the spider, connects to the database, and inserts the data.

1. **Install Database Driver:**  
   Bash  
   pip install psycopg2-binary sqlalchemy

2. **Configure the Pipeline in settings.py:**  
   Python  
   \# In news\_scraper/settings.py

   \# Enable the pipeline and set its order  
   ITEM\_PIPELINES \= {  
      'news\_scraper.pipelines.DatabasePipeline': 300,  
   }

   \# Store the database connection string securely (e.g., in an environment variable)  
   DATABASE\_URL \= "postgresql://user:password@host/dbname?sslmode=require"

3. **Implement the Pipeline Logic in pipelines.py:**

Python

\# In news\_scraper/pipelines.py  
from sqlalchemy import create\_engine, Table, Column, Integer, String, DateTime, MetaData  
from sqlalchemy.orm import sessionmaker  
from sqlalchemy.exc import IntegrityError  
import os

class DatabasePipeline:  
    def \_\_init\_\_(self):  
        \# Get DB URL from settings or environment variable  
        db\_url \= os.environ.get('DATABASE\_URL', 'YOUR\_FALLBACK\_DATABASE\_URL\_HERE')  
        self.engine \= create\_engine(db\_url)  
        self.metadata \= MetaData()

        \# Define the table schema  
        self.articles \= Table('articles', self.metadata,  
            Column('id', Integer, primary\_key=True, autoincrement=True),  
            Column('url', String, unique=True, nullable=False),  
            Column('title', String, nullable=False),  
            Column('publication\_date', DateTime, nullable=True),  
            Column('summary', String, nullable=True)  
        )  
          
        \# Create the table if it doesn't exist  
        self.metadata.create\_all(self.engine)  
          
        Session \= sessionmaker(bind=self.engine)  
        self.session \= Session()

    def process\_item(self, item, spider):  
        \# Create an insert statement, ignoring conflicts on the unique URL  
        \# This prevents duplicate entries from being inserted  
        insert\_statement \= self.articles.insert().values(  
            url=item.get('url'),  
            title=item.get('title'),  
            publication\_date=item.get('publication\_date'),  
            summary=item.get('summary')  
        )

        try:  
            self.session.execute(insert\_statement)  
            self.session.commit()  
        except IntegrityError:  
            self.session.rollback()  
            spider.logger.warning(f"Duplicate item found: {item\['url'\]}")  
        except Exception as e:  
            self.session.rollback()  
            spider.logger.error(f"Failed to insert item into DB: {e}")  
          
        return item

    def close\_spider(self, spider):  
        self.session.close()

This pipeline establishes a connection when the spider starts, defines the database table schema, and attempts to insert each scraped item. By using a UNIQUE constraint on the article url, it gracefully handles duplicate articles that might be discovered multiple times, ensuring data integrity.5

---

## **Part VI: Serving the Data: Building a Performant, Zero-Cost API with FastAPI**

With news data being continuously collected and stored, the final component is a public-facing API to make this data accessible. FastAPI is the optimal choice for this task due to its exceptional performance, which rivals that of NodeJS and Go frameworks, and its modern, developer-friendly features built on standard Python type hints.13

### **Introduction to FastAPI**

FastAPI's key advantages include:

* **High Performance:** It is one of the fastest Python web frameworks available, thanks to its asynchronous capabilities built on Starlette and ASGI.  
* **Data Validation:** It uses Pydantic for data validation. By simply defining data models using Python type hints, FastAPI automatically validates incoming requests and serializes outgoing responses.  
* **Automatic Interactive Documentation:** FastAPI automatically generates interactive API documentation based on the OpenAPI (formerly Swagger) and JSON Schema standards. This creates a user-friendly interface (accessible at /docs by default) where users can explore and test the API endpoints directly from their browser.21

### **API Scaffolding and Database Integration**

The API will be built as a single Python file (main.py) that connects to the same cloud database used by the scraper. It will use SQLModel, a library that combines SQLAlchemy and Pydantic, to interact with the database and define API data models in a single, unified syntax.72

First, install the necessary libraries:

Bash

pip install "fastapi\[all\]" sqlmodel psycopg2-binary

The following is a complete, commented script for the API application.

Python

\# In main.py  
import os  
from typing import List, Optional  
from fastapi import FastAPI, Depends, HTTPException, status  
from sqlmodel import Field, Session, SQLModel, create\_engine, select

\# \--- Database Model Definition \---  
\# This model represents the 'articles' table in the database.  
\# It's used by SQLAlchemy to interact with the DB and by Pydantic for API responses.  
class Article(SQLModel, table=True):  
    id: Optional\[int\] \= Field(default=None, primary\_key=True)  
    url: str \= Field(index=True, unique=True)  
    title: str  
    publication\_date: Optional\[str\] \= None \# Using str for simplicity in API  
    summary: Optional\[str\] \= None

\# \--- Database Connection Setup \---  
\# Get the database URL from an environment variable for security  
DATABASE\_URL \= os.environ.get("DATABASE\_URL", "sqlite:///database.db")

\# The connect\_args are specific to SQLite and not needed for PostgreSQL (like Neon)  
connect\_args \= {"check\_same\_thread": False} if "sqlite" in DATABASE\_URL else {}  
engine \= create\_engine(DATABASE\_URL, echo=True, connect\_args=connect\_args)

def create\_db\_and\_tables():  
    SQLModel.metadata.create\_all(engine)

\# \--- Dependency for Database Session \---  
def get\_session():  
    with Session(engine) as session:  
        yield session

\# \--- FastAPI Application Initialization \---  
app \= FastAPI(  
    title="Zero-Cost News API",  
    description="An API to serve news articles scraped from various sources.",  
    version="1.0.0"  
)

\# Create database tables on application startup  
@app.on\_event("startup")  
def on\_startup():  
    create\_db\_and\_tables()

\# \--- API Endpoints \---  
@app.get("/")  
def read\_root():  
    return {"message": "Welcome to the Zero-Cost News API. Go to /docs for documentation."}

@app.get("/articles/", response\_model=List\[Article\])  
def read\_articles(session: Session \= Depends(get\_session), skip: int \= 0, limit: int \= 100):  
    """  
    Retrieve a list of articles with pagination.  
    """  
    statement \= select(Article).offset(skip).limit(limit)  
    articles \= session.exec(statement).all()  
    return articles

@app.get("/articles/{article\_id}", response\_model=Article)  
def read\_article(article\_id: int, session: Session \= Depends(get\_session)):  
    """  
    Retrieve a single article by its unique ID.  
    """  
    article \= session.get(Article, article\_id)  
    if not article:  
        raise HTTPException(status\_code=status.HTTP\_404\_NOT\_FOUND, detail="Article not found")  
    return article

@app.get("/search/", response\_model=List\[Article\])  
def search\_articles(query: str, session: Session \= Depends(get\_session)):  
    """  
    Search for articles with a title containing the query string.  
    """  
    statement \= select(Article).where(Article.title.contains(query))  
    articles \= session.exec(statement).all()  
    return articles

This script sets up the database connection, defines the data model that FastAPI will use for responses, and creates several API endpoints for interacting with the data.73

### **Defining API Endpoints**

The script defines four endpoints:

1. **GET /**: A root endpoint that provides a welcome message.  
2. **GET /articles/**: Retrieves a list of all articles. It supports pagination through skip and limit query parameters, preventing excessively large responses. The response\_model ensures the output conforms to a list of Article objects.  
3. **GET /articles/{article\_id}**: Fetches a single article by its primary key (id). If no article with the given ID is found, it returns a standard 404 Not Found error.  
4. **GET /search/**: A basic search functionality that allows users to find articles where the title contains a specific query string.

To run this API locally for testing, use Uvicorn:

Bash

uvicorn main:app \--reload

Navigate to http://127.0.0.1:8000/docs in your browser to see the auto-generated, interactive documentation.

---

## **Part VII: Continuous Operation: Automated Deployment and Scheduling**

With the scraper, database, and API components developed, the final step is to deploy them into a cohesive, automated system that runs continuously without manual intervention. This is achieved by leveraging the free tiers of cloud services for scheduling and hosting.

### **The Automation Engine: GitHub Actions**

GitHub Actions is a continuous integration and continuous deployment (CI/CD) platform that allows for the automation of software workflows directly within a GitHub repository. For this project, it serves as the perfect zero-cost scheduling engine. Instead of maintaining an always-on server to run a cron job, a GitHub Actions workflow can be configured to run the Scrapy spider on a recurring schedule (e.g., every hour or every day) in a clean, serverless environment provided by GitHub.24

### **Workflow Configuration: Scheduling the Scraper**

To schedule the scraper, create a YAML file at .github/workflows/scrape.yml within the project repository. This file defines the workflow, its trigger, and the sequence of jobs to be executed.

YAML

\# In.github/workflows/scrape.yml

name: Scheduled News Scraping

on:  
  \# Trigger the workflow on a schedule using cron syntax  
  schedule:  
    \# Runs every hour at the 0th minute  
    \- cron: '0 \* \* \* \*'  
  \# Allows manual triggering from the GitHub Actions UI  
  workflow\_dispatch:

jobs:  
  scrape:  
    runs-on: ubuntu-latest

    steps:  
      \# Step 1: Check out the repository code  
      \- name: Checkout repository  
        uses: actions/checkout@v4

      \# Step 2: Set up Python environment  
      \- name: Set up Python  
        uses: actions/setup-python@v5  
        with:  
          python-version: '3.10'

      \# Step 3: Install project dependencies  
      \- name: Install dependencies  
        run: |  
          python \-m pip install \--upgrade pip  
          pip install \-r requirements.txt  
        
      \# Step 4: Run the Scrapy spider  
      \- name: Run Scraper  
        env:  
          \# Pass the database URL as a secret environment variable  
          DATABASE\_URL: ${{ secrets.DATABASE\_URL }}  
        run: |  
          \# The 'urls' argument should be dynamically generated by a discovery script  
          \# For simplicity, a static list is shown here.  
          \# In a real implementation, a preliminary script would run to get fresh URLs.  
          URLS\_TO\_SCRAPE="http://news.ycombinator.com/rss,https://example.com/rss"  
          scrapy crawl news\_spider \-a urls=$URLS\_TO\_SCRAPE

This workflow configuration automates the entire scraping process 24:

* **on.schedule**: The cron syntax '0 \* \* \* \*' triggers the workflow at the beginning of every hour.24  
* **jobs.scrape.steps**: The sequence of steps ensures a consistent environment for each run. It checks out the code, installs the correct Python version and dependencies from requirements.txt, and finally executes the scrapy crawl command.76  
* **Security with GitHub Secrets:** The database connection string is a sensitive credential. Instead of hardcoding it, it is stored as an encrypted "Secret" in the GitHub repository's settings (Settings \> Secrets and variables \> Actions). The workflow then securely injects this secret into the environment as DATABASE\_URL, which the Scrapy pipeline can access.24

### **Deployment Strategy: Hosting the API for Free**

While GitHub Actions is ideal for scheduled, short-lived tasks like running the scraper, a different solution is needed for the API, which must be running continuously to accept incoming requests. Several Platform-as-a-Service (PaaS) providers offer "forever free" tiers suitable for this purpose.

* **Historical Context (Heroku):** Heroku was once the go-to platform for free application hosting. However, in late 2022, it discontinued its free dyno and database tiers, making it no longer a viable option for zero-cost projects.77  
* **Recommended Platforms (PythonAnywhere, Render):**  
  * **PythonAnywhere:** Offers a "Beginner" free tier that is specifically designed for hosting Python web applications. It provides a persistent file system and a web server that is always on. However, it has significant limitations, including a low CPU allowance (100 seconds/day), restricted outbound internet access (requiring a whitelist for API calls), and a non-custom domain (your-username.pythonanywhere.com).26  
  * **Render:** Provides a free tier for web services that includes 512 MB of RAM and a shared CPU. A key feature is that free services spin down after 15 minutes of inactivity and spin back up when a new request comes in, which can cause a slight initial delay but is highly cost-effective.77

**Deployment to PythonAnywhere (Example):**

1. **Sign up** for a free Beginner account on PythonAnywhere.  
2. **Upload Code:** Upload your API code (main.py) and requirements.txt file to the PythonAnywhere file system.  
3. **Create a Web App:** In the "Web" tab, create a new web app. Select the "FastAPI" framework.  
4. **Configure WSGI File:** PythonAnywhere will generate a WSGI configuration file. Ensure it correctly points to your FastAPI application instance (e.g., from main import app as application).  
5. **Set Environment Variables:** In the "Web" tab, go to the "Configuration" section and set the DATABASE\_URL environment variable to the connection string for your Neon database.  
6. **Install Dependencies:** Open a Bash console in PythonAnywhere and run pip install \-r requirements.txt within a virtual environment.  
7. **Reload Web App:** Reload the web app from the "Web" tab. Your API will now be live at your-username.pythonanywhere.com.

This hybrid deployment model—using GitHub Actions for scheduled computation and a PaaS for continuous serving—is a powerful and cost-effective strategy for operating the entire pipeline at zero cost.

---

## **Part VIII: System Robustness: Monitoring, Logging, and Maintenance**

A system designed for continuous, autonomous operation is only as good as its ability to handle errors and provide visibility into its health. For a scraping pipeline built on a foundation of free services and dependent on external websites, which can change without notice, robust monitoring and logging are not optional—they are essential for long-term stability.

### **Implementing Comprehensive Logging**

Effective logging is the first step toward understanding and debugging system behavior. Both Scrapy and FastAPI have powerful built-in logging capabilities.

* **Scrapy Logging:** Scrapy provides detailed logs about its operations, including requests made, responses received, items scraped, and any errors encountered. To make these logs persistent and useful for debugging, configure Scrapy to write to a file in settings.py:  
  Python  
  \# In news\_scraper/settings.py  
  LOG\_LEVEL \= 'INFO'  \# Set the desired log level (DEBUG, INFO, WARNING, ERROR)  
  LOG\_FILE \= 'scrapy\_log.txt' \# Specify the file to store logs  
  LOG\_ENCODING \= 'utf-8'  
  LOG\_STDOUT \= True \# Also print logs to standard output for GitHub Actions logs

  This configuration will create a log file that captures the outcome of each scraping run, which is invaluable for diagnosing failures.80  
* **FastAPI Logging:** FastAPI is built on Starlette, which integrates with Python's standard logging module. By default, Uvicorn (the server running the app) will log requests and errors to the console. For a deployed application, these logs can be captured by the hosting platform (e.g., PythonAnywhere's log files) for later review.

### **Zero-Cost Monitoring and Alerting**

Proactive monitoring is critical for detecting failures before they lead to significant data gaps. While many commercial monitoring solutions exist, a highly effective, zero-cost alerting system can be built using the tools already in the technology stack.

The GitHub Actions workflow that runs the scraper provides a perfect opportunity for monitoring. A workflow job fails if any of its steps exits with a non-zero status code. This behavior can be leveraged to create an automated alerting loop.

1. **Error Handling in the Script:** Ensure the Python scraper script is designed to exit with an error code if a critical failure occurs (e.g., it cannot connect to the database or fails to scrape any items).  
2. **Workflow Alerting Step:** Add a conditional step to the scrape.yml workflow that only runs if a preceding step has failed. This step can use a pre-built GitHub Action to send an email notification.

YAML

\# In.github/workflows/scrape.yml (add this step at the end of the job)  
      \- name: Send email on failure  
        if: failure() \# This condition ensures the step only runs if a previous step failed  
        uses: dawidd6/action-send-mail@v3  
        with:  
          server\_address: smtp.gmail.com  
          server\_port: 465  
          username: ${{ secrets.MAIL\_USERNAME }}  
          password: ${{ secrets.MAIL\_PASSWORD }}  
          subject: 'GitHub Actions: Scraper Workflow Failed'  
          to: your-email@example.com  
          from: GitHub Actions \<github-actions@example.com\>  
          body: |  
            The news scraper workflow in ${{ github.repository }} has failed.  
            Run ID: ${{ github.run\_id }}  
            Check the logs for details: ${{ github.server\_url }}/${{ github.repository }}/actions/runs/${{ github.run\_id }}

To use this, you would need to set up MAIL\_USERNAME and MAIL\_PASSWORD as secrets in your GitHub repository (an app-specific password for Gmail is recommended). This creates a powerful, event-driven, and entirely free monitoring system that provides immediate notification of scraper failures, allowing for rapid response and debugging.82

### **Long-Term Maintenance: The Reality of "Scraper Rot"**

Web scrapers are inherently fragile. Websites frequently undergo redesigns, which can change HTML structures, class names, and element IDs. When this happens, the CSS or XPath selectors used by the scraper will no longer find the target data, causing the scraper to fail. This phenomenon is known as "scraper rot".81

A continuous system must have a strategy for dealing with this inevitability:

* **Write Resilient Selectors:** When possible, avoid overly specific selectors that are likely to change. For example, div.article-content \> div \> p:nth-child(2) is more fragile than a selector that targets a more stable class name like p.article-summary.  
* **Regular Log Review:** Periodically review the scraper logs generated by GitHub Actions. A sudden increase in errors or a drop in the number of items scraped for a particular source is a strong indicator that the target website has changed.  
* **Modular Spider Design:** By creating separate spiders (or separate parsing logic within a single spider) for each news source, a change in one website will not break the entire system. This modularity makes it easier to identify and fix the specific part of the code that needs updating.

Maintenance is an ongoing process. A "set it and forget it" mindset is unrealistic; a "monitor and maintain" approach, supported by automated logging and alerting, is essential for the long-term success of the project.

---

## **Part IX: Legal and Ethical Framework for Web Scraping**

Building a web scraper carries with it significant legal and ethical responsibilities. Operating an automated system that interacts with third-party websites requires a clear understanding of the rules to ensure the project is both sustainable and lawful.

### **Navigating the Legal Landscape**

The legality of web scraping is a complex and evolving area, but several key legal principles and precedents provide guidance. In the United States, the legal status generally hinges on three areas: the Computer Fraud and Abuse Act (CFAA), contract law (Terms of Service), and copyright law.

* **Computer Fraud and Abuse Act (CFAA):** The CFAA is a federal anti-hacking law that prohibits accessing a computer "without authorization." For years, companies argued that scraping in violation of their Terms of Service constituted unauthorized access. However, the landmark case *LinkedIn Corp. v. hiQ Labs, Inc.* (2019, reaffirmed 2022\) established a crucial precedent. The courts ruled that scraping data that is publicly accessible on the internet (i.e., does not require a password or login) does not violate the CFAA. This decision significantly clarified that scraping public data is generally considered legal under this statute.48  
* **Terms of Service (ToS):** While scraping public data may not violate the CFAA, it can still be a breach of contract if the website's Terms of Service explicitly prohibit it. When you create an account or otherwise click "I agree," you are entering into a legally binding contract (a "clickwrap" agreement). Violating these terms can lead to legal action for breach of contract.83 For publicly accessible data where no such agreement is made, the enforceability of ToS is less clear, but it remains a legal risk.  
* **Copyright Law:** Copyright law protects original works of authorship, such as the full text of a news article. However, it does not protect raw facts. Data points like a headline, a publication date, or a product price are generally considered facts and are not copyrightable.83 Scraping and storing these facts is typically permissible. However, scraping and republishing substantial portions of copyrighted text (like the full body of an article) could constitute copyright infringement. The doctrine of "fair use" may apply if the use is transformative (e.g., for analysis or research), but this is a complex, case-by-case determination.83

### **A Checklist for Responsible Scraping**

To operate the news scraping system ethically and minimize legal risk, adhere to the following best practices, which synthesize the technical and legal considerations discussed throughout this report.

1. **Prioritize Official APIs:** Before scraping, always check if the website offers a public API. An API is an explicit invitation to access data programmatically and is always the preferred method.84  
2. **Respect robots.txt:** Always obey the directives in the robots.txt file. Do not scrape pages that are explicitly disallowed. Keep Scrapy's ROBOTSTXT\_OBEY setting enabled.47  
3. **Scrape Public Data Only:** Do not attempt to scrape information that is behind a login, paywall, or any other access control system. This is the clearest line between permissible and potentially illegal activity under the CFAA.48  
4. **Be a Polite Crawler:** Scrape at a slow, reasonable rate. Use randomized delays between requests and limit concurrency to avoid placing an undue burden on the website's servers. Identify your bot with a legitimate User-Agent string that includes contact information.84  
5. **Take Only What You Need:** Configure the scraper to extract only the specific data points required for the project (highlights, publication times). Do not download entire pages or assets like images and videos unnecessarily.48  
6. **Do Not Republish Verbatim:** The API should serve the extracted headlines, summaries, and links back to the original articles. Do not store or serve the full, copyrighted text of the articles, as this poses a significant copyright risk.83  
7. **Secure Your Data:** Store the collected data securely in the database with proper access controls. Do not expose the raw scraped data publicly.84  
8. **Stay Informed:** The legal landscape can change. Regularly review the Terms of Service of your target sites and stay aware of new legal precedents in the area of web scraping.47

By following this comprehensive blueprint, it is possible to build a powerful, stable, and continuous news aggregation system entirely at zero cost. Success hinges not on financial resources, but on a commitment to intelligent architectural design, efficient implementation, and responsible, ethical operation.

#### **Geciteerd werk**

1. Best practices for XML sitemaps and RSS/Atom feeds | Google Search Central Blog, geopend op augustus 2, 2025, [https://developers.google.com/search/blog/2014/10/best-practices-for-xml-sitemaps-rssatom](https://developers.google.com/search/blog/2014/10/best-practices-for-xml-sitemaps-rssatom)  
2. Fundus: A Simple-to-Use News Scraper Optimized for High Quality Extractions \- arXiv, geopend op augustus 2, 2025, [https://arxiv.org/html/2403.15279v1](https://arxiv.org/html/2403.15279v1)  
3. Scrapy vs. Beautiful Soup: A Comparison of Web Scraping Tools \- Oxylabs, geopend op augustus 2, 2025, [https://oxylabs.io/blog/scrapy-vs-beautifulsoup](https://oxylabs.io/blog/scrapy-vs-beautifulsoup)  
4. Web Scraping With Scrapy: The Complete Guide in 2025 \- Scrapfly, geopend op augustus 2, 2025, [https://scrapfly.io/blog/posts/web-scraping-with-scrapy](https://scrapfly.io/blog/posts/web-scraping-with-scrapy)  
5. Data Storage for Web Scraping: A Comprehensive Guide \- Scrapeless, geopend op augustus 2, 2025, [https://www.scrapeless.com/en/blog/data-storage](https://www.scrapeless.com/en/blog/data-storage)  
6. Build vs. Buy: Web Scraping Cost Analysis \- SOAX, geopend op augustus 2, 2025, [https://soax.com/blog/build-vs-buy-web-scraping-cost-analysis](https://soax.com/blog/build-vs-buy-web-scraping-cost-analysis)  
7. The Best Web Scraping APIs for 2025 \- Proxyway, geopend op augustus 2, 2025, [https://proxyway.com/best/best-web-scraping-apis](https://proxyway.com/best/best-web-scraping-apis)  
8. Best Scraper API (best web scraping API) of 2025 | TechRadar, geopend op augustus 2, 2025, [https://www.techradar.com/pro/software-services/best-scraper-api-best-web-scraping-api-of-year](https://www.techradar.com/pro/software-services/best-scraper-api-best-web-scraping-api-of-year)  
9. Scrapy, geopend op augustus 2, 2025, [https://www.scrapy.org/](https://www.scrapy.org/)  
10. Scrapy 2.13 documentation — Scrapy 2.13.3 documentation, geopend op augustus 2, 2025, [https://docs.scrapy.org/](https://docs.scrapy.org/)  
11. Neon Pricing, geopend op augustus 2, 2025, [https://neon.com/pricing](https://neon.com/pricing)  
12. Neon plans \- Neon Docs, geopend op augustus 2, 2025, [https://neon.com/docs/introduction/plans](https://neon.com/docs/introduction/plans)  
13. First Steps \- FastAPI \- Tiangolo, geopend op augustus 2, 2025, [https://fastapi.tiangolo.com/tutorial/first-steps/](https://fastapi.tiangolo.com/tutorial/first-steps/)  
14. Scrapy vs. Beautiful Soup for web scraping \- Apify Blog, geopend op augustus 2, 2025, [https://blog.apify.com/beautiful-soup-vs-scrapy-web-scraping/](https://blog.apify.com/beautiful-soup-vs-scrapy-web-scraping/)  
15. Python Scrapy vs Requests with Beautiful Soup Compared \- ScrapeOps, geopend op augustus 2, 2025, [https://scrapeops.io/python-web-scraping-playbook/python-scrapy-vs-requests-beautiful-soup/](https://scrapeops.io/python-web-scraping-playbook/python-scrapy-vs-requests-beautiful-soup/)  
16. Scrapy vs BeautifulSoup: Which Is Better For You? \- ZenRows, geopend op augustus 2, 2025, [https://www.zenrows.com/blog/scrapy-vs-beautifulsoup](https://www.zenrows.com/blog/scrapy-vs-beautifulsoup)  
17. SQLite with Python \- Tutorialspoint, geopend op augustus 2, 2025, [https://www.tutorialspoint.com/sqlite/sqlite\_python.htm](https://www.tutorialspoint.com/sqlite/sqlite_python.htm)  
18. Python SQLite \- GeeksforGeeks, geopend op augustus 2, 2025, [https://www.geeksforgeeks.org/python/python-sqlite/](https://www.geeksforgeeks.org/python/python-sqlite/)  
19. Pricing | MongoDB, geopend op augustus 2, 2025, [https://www.mongodb.com/pricing](https://www.mongodb.com/pricing)  
20. MongoDB Limits and Thresholds \- Database Manual, geopend op augustus 2, 2025, [https://www.mongodb.com/docs/manual/reference/limits/](https://www.mongodb.com/docs/manual/reference/limits/)  
21. Tutorial \- User Guide \- FastAPI \- Tiangolo, geopend op augustus 2, 2025, [https://fastapi.tiangolo.com/tutorial/](https://fastapi.tiangolo.com/tutorial/)  
22. Tutorial — Flask Documentation (3.1.x), geopend op augustus 2, 2025, [https://flask.palletsprojects.com/en/stable/tutorial/](https://flask.palletsprojects.com/en/stable/tutorial/)  
23. Flask Tutorial \- GeeksforGeeks, geopend op augustus 2, 2025, [https://www.geeksforgeeks.org/python/flask-tutorial/](https://www.geeksforgeeks.org/python/flask-tutorial/)  
24. How to schedule Python scripts with GitHub Actions \- Python Engineer, geopend op augustus 2, 2025, [https://www.python-engineer.com/posts/run-python-github-actions/](https://www.python-engineer.com/posts/run-python-github-actions/)  
25. PythonAnywhere: Host, run, and code Python in the cloud, geopend op augustus 2, 2025, [https://www.pythonanywhere.com/](https://www.pythonanywhere.com/)  
26. Plans and pricing : PythonAnywhere, geopend op augustus 2, 2025, [https://www.pythonanywhere.com/pricing/](https://www.pythonanywhere.com/pricing/)  
27. Automating Web Scraping with Cron Jobs and Schedulers, geopend op augustus 2, 2025, [https://web.instantapi.ai/blog/automating-web-scraping-with-cron-jobs-and-schedulers/](https://web.instantapi.ai/blog/automating-web-scraping-with-cron-jobs-and-schedulers/)  
28. Webscraper that scrapes every hour : r/datascience \- Reddit, geopend op augustus 2, 2025, [https://www.reddit.com/r/datascience/comments/tuwbi1/webscraper\_that\_scrapes\_every\_hour/](https://www.reddit.com/r/datascience/comments/tuwbi1/webscraper_that_scrapes_every_hour/)  
29. How to Find a Website's Sitemap \- Seer Interactive, geopend op augustus 2, 2025, [https://www.seerinteractive.com/insights/how-to-find-your-sitemap](https://www.seerinteractive.com/insights/how-to-find-your-sitemap)  
30. Build and Submit a Sitemap | Google Search Central | Documentation, geopend op augustus 2, 2025, [https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)  
31. RSS / XML Scraper \- Apify, geopend op augustus 2, 2025, [https://apify.com/jupri/rss-xml-scraper](https://apify.com/jupri/rss-xml-scraper)  
32. How to Find RSS Feed URLs | Help Center \- Ocoya, geopend op augustus 2, 2025, [https://help.ocoya.com/en/articles/8021127-how-to-find-rss-feed-urls](https://help.ocoya.com/en/articles/8021127-how-to-find-rss-feed-urls)  
33. How to Find the Sitemap of a Website (7 Options) \- SEOcrawl, geopend op augustus 2, 2025, [https://seocrawl.com/en/how-to-find-a-sitemap/](https://seocrawl.com/en/how-to-find-a-sitemap/)  
34. How to Find a Sitemap: Learn 5 Ways, Step-by-Step \- Slickplan, geopend op augustus 2, 2025, [https://slickplan.com/blog/how-to-find-sitemap](https://slickplan.com/blog/how-to-find-sitemap)  
35. RSS Feed URL Finder \- Chrome Web Store, geopend op augustus 2, 2025, [https://chromewebstore.google.com/detail/rss-feed-url-finder/apfhghblgifegckccakakdlbjcdnbjmb](https://chromewebstore.google.com/detail/rss-feed-url-finder/apfhghblgifegckccakakdlbjcdnbjmb)  
36. Feedparser: Python package for reading RSS feeds \- Meet Gor, geopend op augustus 2, 2025, [https://mr-destructive.github.io/techstructive-blog/python-feedparser/](https://mr-destructive.github.io/techstructive-blog/python-feedparser/)  
37. feedparser \- PyPI, geopend op augustus 2, 2025, [https://pypi.org/project/feedparser/](https://pypi.org/project/feedparser/)  
38. Extract feed details from RSS in Python \- GeeksforGeeks, geopend op augustus 2, 2025, [https://www.geeksforgeeks.org/python/extract-feed-details-from-rss-in-python/](https://www.geeksforgeeks.org/python/extract-feed-details-from-rss-in-python/)  
39. Build an RSS Feed Reader in Python Using feedparser \- Codevisionz, geopend op augustus 2, 2025, [https://codevisionz.com/lessons/python-rss-feed-reader-example/](https://codevisionz.com/lessons/python-rss-feed-reader-example/)  
40. ultimate-sitemap-parser \- PyPI, geopend op augustus 2, 2025, [https://pypi.org/project/ultimate-sitemap-parser/](https://pypi.org/project/ultimate-sitemap-parser/)  
41. The Easy Way to Crawl Sitemaps with Python \- ProxyScrape, geopend op augustus 2, 2025, [https://pt-br.proxyscrape.com/blog/the-easy-way-to-crawl-siteemaps-with-python](https://pt-br.proxyscrape.com/blog/the-easy-way-to-crawl-siteemaps-with-python)  
42. Web Scraping with Scrapy: Python Tutorial \- Oxylabs, geopend op augustus 2, 2025, [https://oxylabs.io/blog/scrapy-web-scraping-tutorial](https://oxylabs.io/blog/scrapy-web-scraping-tutorial)  
43. Scrapy Tutorial — Scrapy 2.13.3 documentation, geopend op augustus 2, 2025, [https://docs.scrapy.org/en/latest/intro/tutorial.html](https://docs.scrapy.org/en/latest/intro/tutorial.html)  
44. Implementing Web Scraping in Python with Scrapy \- GeeksforGeeks, geopend op augustus 2, 2025, [https://www.geeksforgeeks.org/python/implementing-web-scraping-python-scrapy/](https://www.geeksforgeeks.org/python/implementing-web-scraping-python-scrapy/)  
45. Headless Browsers vs. API Scraping: When and How to Use Each ..., geopend op augustus 2, 2025, [https://crawlbase.com/blog/headless-browsers-vs-api-scraping/](https://crawlbase.com/blog/headless-browsers-vs-api-scraping/)  
46. Datacenter vs. Residential Proxies: Comparison Guide \- Oxylabs, geopend op augustus 2, 2025, [https://oxylabs.io/blog/the-difference-between-data-center-and-residential-proxies](https://oxylabs.io/blog/the-difference-between-data-center-and-residential-proxies)  
47. Web Scraping Ethics: Adhering to Legal and Ethical Guidelines ..., geopend op augustus 2, 2025, [https://moldstud.com/articles/p-web-scraping-ethics-adhering-to-legal-and-ethical-guidelines](https://moldstud.com/articles/p-web-scraping-ethics-adhering-to-legal-and-ethical-guidelines)  
48. Is Web Scraping Legal? Laws, Ethics, and Best Practices, geopend op augustus 2, 2025, [https://research.aimultiple.com/is-web-scraping-legal/](https://research.aimultiple.com/is-web-scraping-legal/)  
49. Top List of User Agents for Web Scraping & Tips \- ZenRows, geopend op augustus 2, 2025, [https://www.zenrows.com/blog/user-agent-web-scraping](https://www.zenrows.com/blog/user-agent-web-scraping)  
50. How to Effectively Use User Agents for Web Scraping \- Scrapfly, geopend op augustus 2, 2025, [https://scrapfly.io/blog/posts/user-agent-header-in-web-scraping](https://scrapfly.io/blog/posts/user-agent-header-in-web-scraping)  
51. Web Scraping Guide \- Headers & User-Agents Optimization ..., geopend op augustus 2, 2025, [https://scrapeops.io/web-scraping-playbook/web-scraping-guide-header-user-agents/](https://scrapeops.io/web-scraping-playbook/web-scraping-guide-header-user-agents/)  
52. How To Use Python To Fake and Rotate User-Agents \- ScrapeHero, geopend op augustus 2, 2025, [https://www.scrapehero.com/how-to-fake-and-rotate-user-agents-using-python-3/](https://www.scrapehero.com/how-to-fake-and-rotate-user-agents-using-python-3/)  
53. Selenium vs. BeautifulSoup in 2025: Which to Choose? \- Oxylabs, geopend op augustus 2, 2025, [https://oxylabs.io/blog/selenium-vs-beautifulsoup](https://oxylabs.io/blog/selenium-vs-beautifulsoup)  
54. Scrape Content from Dynamic Websites \- GeeksforGeeks, geopend op augustus 2, 2025, [https://www.geeksforgeeks.org/python/scrape-content-from-dynamic-websites/](https://www.geeksforgeeks.org/python/scrape-content-from-dynamic-websites/)  
55. 8 best Python web scraping libraries in 2025 \- Apify Blog, geopend op augustus 2, 2025, [https://blog.apify.com/what-are-the-best-python-web-scraping-libraries/](https://blog.apify.com/what-are-the-best-python-web-scraping-libraries/)  
56. Scraping JavaScript-Rendered Web Pages With Python: Complete Guide 2025 \- ZenRows, geopend op augustus 2, 2025, [https://www.zenrows.com/blog/scraping-javascript-rendered-web-pages](https://www.zenrows.com/blog/scraping-javascript-rendered-web-pages)  
57. How do you go about web scraping dynamic pages? : r/learnpython \- Reddit, geopend op augustus 2, 2025, [https://www.reddit.com/r/learnpython/comments/1hoir54/how\_do\_you\_go\_about\_web\_scraping\_dynamic\_pages/](https://www.reddit.com/r/learnpython/comments/1hoir54/how_do_you_go_about_web_scraping_dynamic_pages/)  
58. Scrape a JavaScript heavy website with requests+bs4 \- Stack Overflow, geopend op augustus 2, 2025, [https://stackoverflow.com/questions/73364717/scrape-a-javascript-heavy-website-with-requestsbs4](https://stackoverflow.com/questions/73364717/scrape-a-javascript-heavy-website-with-requestsbs4)  
59. Selecting dynamically-loaded content — Scrapy 2.13.3 documentation, geopend op augustus 2, 2025, [https://docs.scrapy.org/en/latest/topics/dynamic-content.html](https://docs.scrapy.org/en/latest/topics/dynamic-content.html)  
60. What Is a Rotating ProxyWhat Is a Rotating Proxy? Benefits, Use ..., geopend op augustus 2, 2025, [https://www.joinmassive.com/blog/what-is-a-rotating-proxy](https://www.joinmassive.com/blog/what-is-a-rotating-proxy)  
61. 7 best tools for browser fingerprint evasion in web scraping for 2025, geopend op augustus 2, 2025, [https://soax.com/blog/prevent-browser-fingerprinting](https://soax.com/blog/prevent-browser-fingerprinting)  
62. What Is Browser Fingerprinting and How to Bypass it? \- ZenRows, geopend op augustus 2, 2025, [https://www.zenrows.com/blog/browser-fingerprinting](https://www.zenrows.com/blog/browser-fingerprinting)  
63. What Is Device Fingerprinting and How to Bypass It \- ZenRows, geopend op augustus 2, 2025, [https://www.zenrows.com/blog/device-fingerprint](https://www.zenrows.com/blog/device-fingerprint)  
64. A Full Guide on Bypassing CAPTCHA for Web Scraping | Octoparse, geopend op augustus 2, 2025, [https://www.octoparse.com/blog/5-things-you-need-to-know-of-bypassing-captcha-for-web-scraping](https://www.octoparse.com/blog/5-things-you-need-to-know-of-bypassing-captcha-for-web-scraping)  
65. Handling CAPTCHAs in Web Scraping: Tools and Techniques \- VOCSO Technologies, geopend op augustus 2, 2025, [https://www.vocso.com/blog/handling-captchas-in-web-scraping-tools-and-techniques/](https://www.vocso.com/blog/handling-captchas-in-web-scraping-tools-and-techniques/)  
66. Datacenter vs. Residential Proxies: 13 Key Differences \- Webshare, geopend op augustus 2, 2025, [https://www.webshare.io/blog/datacenter-vs-residential-proxies](https://www.webshare.io/blog/datacenter-vs-residential-proxies)  
67. Web scraping: How do I store data? : r/AskProgramming \- Reddit, geopend op augustus 2, 2025, [https://www.reddit.com/r/AskProgramming/comments/s09ag6/web\_scraping\_how\_do\_i\_store\_data/](https://www.reddit.com/r/AskProgramming/comments/s09ag6/web_scraping_how_do_i_store_data/)  
68. Best way to store scraped data in Python for analysis \- Stack Overflow, geopend op augustus 2, 2025, [https://stackoverflow.com/questions/38661144/best-way-to-store-scraped-data-in-python-for-analysis](https://stackoverflow.com/questions/38661144/best-way-to-store-scraped-data-in-python-for-analysis)  
69. Free databases, geopend op augustus 2, 2025, [https://free-databases.vercel.app/](https://free-databases.vercel.app/)  
70. End of Life Announcement \- ElephantSQL, geopend op augustus 2, 2025, [https://www.elephantsql.com/blog/end-of-life-announcement.html](https://www.elephantsql.com/blog/end-of-life-announcement.html)  
71. FastAPI for Beginners: Build Powerful APIs in Minutes, geopend op augustus 2, 2025, [https://www.youtube.com/watch?v=rSOPm6-3d\_E](https://www.youtube.com/watch?v=rSOPm6-3d_E)  
72. SQL (Relational) Databases \- FastAPI, geopend op augustus 2, 2025, [https://fastapi.tiangolo.com/tutorial/sql-databases/](https://fastapi.tiangolo.com/tutorial/sql-databases/)  
73. FastAPI \- SQLite Databases \- GeeksforGeeks, geopend op augustus 2, 2025, [https://www.geeksforgeeks.org/python/fastapi-sqlite-databases/](https://www.geeksforgeeks.org/python/fastapi-sqlite-databases/)  
74. FastAPI and SQL Databases: A Detailed Tutorial \- Orchestra, geopend op augustus 2, 2025, [https://www.getorchestra.io/guides/fastapi-and-sql-databases-a-detailed-tutorial](https://www.getorchestra.io/guides/fastapi-and-sql-databases-a-detailed-tutorial)  
75. patrickloeber/python-github-action-template: Schedule a Python script with GitHub Actions, geopend op augustus 2, 2025, [https://github.com/patrickloeber/python-github-action-template](https://github.com/patrickloeber/python-github-action-template)  
76. How to setup github actions to run my python script on schedule? · community · Discussion \#26539, geopend op augustus 2, 2025, [https://github.com/orgs/community/discussions/26539](https://github.com/orgs/community/discussions/26539)  
77. 10 Best Heroku Alternatives & Competitors for 2025 \- Qovery, geopend op augustus 2, 2025, [https://www.qovery.com/blog/best-heroku-alternatives/](https://www.qovery.com/blog/best-heroku-alternatives/)  
78. Heroku outages are getting worse. The best alternative in 2025 with no downtime. | Blog, geopend op augustus 2, 2025, [https://northflank.com/blog/heroku-outage-downtime-status](https://northflank.com/blog/heroku-outage-downtime-status)  
79. PythonAnywhere Reviews 2025: Details, Pricing, & Features \- G2, geopend op augustus 2, 2025, [https://www.g2.com/products/pythonanywhere/reviews](https://www.g2.com/products/pythonanywhere/reviews)  
80. How to create Scalable Web Scraping Pipelines Using Python and Scrapy, geopend op augustus 2, 2025, [https://www.vocso.com/blog/how-to-create-scalable-web-scraping-pipelines-using-python-and-scrapy/](https://www.vocso.com/blog/how-to-create-scalable-web-scraping-pipelines-using-python-and-scrapy/)  
81. A Pipeline-oriented Processing Approach to Continuous and Long-term Web Scraping \- Semantic Scholar, geopend op augustus 2, 2025, [https://pdfs.semanticscholar.org/4ba0/db149ca1f85deb89ddd82851b987fc7ab827.pdf](https://pdfs.semanticscholar.org/4ba0/db149ca1f85deb89ddd82851b987fc7ab827.pdf)  
82. Data Pipeline Monitoring: Best Practices for Full Observability \- Prefect, geopend op augustus 2, 2025, [https://www.prefect.io/blog/data-pipeline-monitoring-best-practices](https://www.prefect.io/blog/data-pipeline-monitoring-best-practices)  
83. Is Web & Data Scraping Legally Allowed? \- Zyte, geopend op augustus 2, 2025, [https://www.zyte.com/learn/is-web-scraping-legal/](https://www.zyte.com/learn/is-web-scraping-legal/)  
84. Ethical Considerations in Web Scraping: Best Practices \- InstantAPI.ai, geopend op augustus 2, 2025, [https://web.instantapi.ai/blog/ethical-considerations-in-web-scraping-best-practices/](https://web.instantapi.ai/blog/ethical-considerations-in-web-scraping-best-practices/)  
85. 2.4. Crawling rules · GitBook, geopend op augustus 2, 2025, [https://codepr.github.io/webcrawler-from-scratch/chapter1/crawling-rules.html](https://codepr.github.io/webcrawler-from-scratch/chapter1/crawling-rules.html)