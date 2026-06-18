\# Business Case



\## Project Title



Amazon Germany Wireless Headphones Price and Competitor Intelligence ETL Pipeline



\## Background



The wireless-headphones market includes established international brands, emerging sellers and unbranded products across several price categories. Customers commonly compare products using price, rating, review volume, Prime availability and sponsored status. These factors also provide useful information for retailers, pricing analysts and category managers.



However, competitor information on Amazon changes frequently. Manually collecting and comparing product information would be slow, inconsistent and difficult to repeat. An automated business-intelligence pipeline provides a more reliable method of collecting, preparing, storing and analysing the data.



\## Business Problem



An electronics retailer wants to understand the competitive position of wireless-headphone products listed on Amazon Germany. The retailer needs visibility into product prices, ratings, customer-review volumes, brand presence, Prime availability and sponsored listings.



The business requires a repeatable process that can collect the latest product data, clean inconsistent values, preserve historical observations and present the results through an interactive dashboard.



\## Project Objective



The objective of this project is to build an automated end-to-end ETL pipeline that:



1\. Extracts wireless-headphone product data from Amazon Germany through the Amazon Scraper API.

2\. Saves the original API response as raw JSON.

3\. Cleans and transforms the data using Python and Pandas.

4\. Stores product and observation data in PostgreSQL.

5\. Automates the pipeline using Windows Task Scheduler.

6\. Analyses the stored data using SQL and Python.

7\. Presents competitor and pricing information through Power BI.



\## Business Questions



The project addresses the following questions:



1\. How many unique wireless-headphone products and brands are represented?

2\. What are the average, minimum and maximum product prices?

3\. Which brands have the highest product presence?

4\. Which brands have the highest average prices and ratings?

5\. How are products distributed across budget, mid-range, premium and luxury categories?

6\. Which products have the highest ratings and review counts?

7\. Are highly rated products always more expensive?

8\. How do Prime and non-Prime products compare?

9\. How do sponsored and organic listings compare?

10\. Which products appear to provide strong value relative to price, rating and review volume?



\## Intended Users



The dashboard is designed for:



\* E-commerce analysts

\* Pricing analysts

\* Category managers

\* Retail managers

\* Product managers

\* Marketing teams



\## Expected Business Value



The solution supports competitor benchmarking, pricing analysis and product-positioning decisions. It also provides a reusable structure for monitoring how product prices, ratings and market visibility change over time.



By separating stable product information from changing observations, the database can preserve multiple extraction periods and support future historical-price analysis.



\## Project Scope



The current project focuses on wireless headphones listed on Amazon Germany. The API response provides product titles, ASINs, prices, ratings, review counts, product links, image links, Prime status and sponsored status.



The selected API response did not provide original prices or search-ranking positions. These fields remain in the database structure so that future API responses can populate them when available.



\## Technology Stack



\* Amazon Scraper API for data collection

\* Python and Pandas for extraction and transformation

\* Jupyter Notebook for development and analysis

\* PostgreSQL and pgAdmin 4 for database storage

\* SQLAlchemy and Psycopg2 for database connectivity

\* Windows Task Scheduler for workflow orchestration

\* Power BI for interactive visualisation

\* Git and GitHub for version control and submission



