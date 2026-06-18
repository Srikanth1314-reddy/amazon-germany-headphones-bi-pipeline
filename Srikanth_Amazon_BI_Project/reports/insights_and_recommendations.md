\# Business Insights and Recommendations



\## Dashboard Overview



The final Power BI dashboard analyses the latest observations for 32 wireless-headphone products listed on Amazon Germany. The dataset contains eight identified brand groups and includes information about current prices, ratings, customer reviews, price categories, Prime status and sponsored status.



The dashboard is divided into two pages:



1\. Market Overview

2\. Competitor Analysis



The analysis is based on the most recent observation available for each product so that repeated ETL executions do not inflate the product-level results.



\## Key Performance Indicators



| KPI                         |               Result |

| --------------------------- | -------------------: |

| Total products              |                   32 |

| Total brands                |                    8 |

| Average price               |               €59.72 |

| Average rating              |                 4.48 |

| Total customer reviews      |              701,407 |

| Average reviews per product | Approximately 22,000 |

| Average value score         |               1.2594 |



\## Key Business Insights



\### 1. The market is concentrated in lower price categories



The Budget category contains 18 of the 32 products, representing more than half of the analysed listings. The Mid-range category contains nine products, while only four products are Premium and one is Luxury.



This indicates that the selected Amazon Germany wireless-headphones market is mainly price competitive. Most sellers appear to target customers seeking affordable products rather than premium alternatives.



\### 2. Product ratings are generally strong



The overall average rating is 4.48 out of 5. Twenty-one products belong to the Good rating category, ten are classified as Excellent and only one product is in the Average category.



This suggests that strong ratings are common in this market. Therefore, a good rating alone may not be enough to differentiate a product from competitors.



\### 3. Customer review volume is highly concentrated



The products collectively account for 701,407 customer reviews, with approximately 22,000 reviews per product on average. However, the Top 10 Products by Review Count chart shows that a small number of listings account for a large share of total review activity.



Several Soundcore products appear among the most-reviewed listings. This indicates strong customer familiarity, established sales history and substantial marketplace visibility for the brand.



\### 4. Unidentified brands represent the largest product group



Twelve products are grouped under the Unknown brand category, making it the largest single group. Among recognised brands, JBL has the highest product presence with seven products, followed by Soundcore with six and Sony with three.



The high Unknown count reflects a limitation in deriving brands from product titles. It may also indicate that Amazon contains many generic or lesser-known sellers competing in the wireless-headphones category.



\### 5. JBL has broad product coverage



JBL has the largest number of products among clearly identified brands. Its listings cover multiple prices and provide a visible competitive presence within the selected search results.



This suggests that JBL follows a broad-market approach by offering several alternatives rather than relying on a single product.



\### 6. Soundcore demonstrates strong review performance



Soundcore appears repeatedly in the chart of products with the highest review counts. This suggests that its products have achieved strong customer adoption and marketplace recognition.



High review counts can create social proof, making it more difficult for newly listed competitors to attract customer attention even when they offer similar prices or ratings.



\### 7. Higher prices do not consistently produce higher ratings



The price-versus-rating scatter chart does not show a clear upward relationship. Most products are concentrated below approximately €100 while maintaining ratings between roughly 4.2 and 4.7.



A much more expensive product is visible at close to €700, but its rating is not substantially higher than many affordable alternatives. This suggests that a higher price does not automatically produce stronger customer satisfaction.



\### 8. Apple has the highest average brand price



The Average Price by Brand chart places Apple at the top of the brand-level price comparison. This reflects premium positioning relative to the other brands in the dataset.



However, the brand comparison also indicates that high average price and high rating do not always move together. Some lower-priced brands achieve ratings close to those of more expensive competitors.



\### 9. Affordable products can provide strong perceived value



The value score combines product rating, review volume and current price. Products with high ratings, substantial review histories and relatively low prices receive stronger scores.



This exploratory measure highlights that customer value is not based on price alone. An affordable product with a strong review history may offer a more attractive competitive position than an expensive product with similar ratings.



\### 10. The market presents a difficult entry environment



Most products already have good or excellent ratings, while several established listings have very large review counts. A new seller may therefore find it difficult to compete using only price or technical specifications.



Successful market entry would require differentiation through product quality, customer service, fulfilment, branding and review generation.



\## Business Recommendations



\### 1. Focus on the Budget and Mid-range segments



A retailer entering this market should prioritise products priced within the Budget and Mid-range categories because these segments contain most of the existing listings.



However, competing only by offering the lowest price may reduce margins. The product should combine competitive pricing with clear quality, warranty and service benefits.



\### 2. Use a value-based positioning strategy



The dashboard shows that higher prices do not always correspond to higher ratings. Retailers should communicate the relationship between product quality and price rather than positioning products as premium only because they are expensive.



Marketing should emphasise practical value such as battery life, sound quality, comfort, durability and warranty support.



\### 3. Benchmark against Soundcore and JBL



Soundcore should be monitored for review strength and customer adoption, while JBL should be monitored for product-range coverage.



Competitors can compare their pricing, ratings and review volumes against these brands to identify gaps in the market.



\### 4. Build customer reviews early



High review counts appear to provide significant marketplace credibility. New products should use ethical review-generation practices such as:



\* Reliable product quality

\* Fast customer support

\* Clear post-purchase communication

\* Easy returns

\* Encouraging verified customers to provide honest feedback



Fake or incentivised reviews should not be used.



\### 5. Improve brand identification in future pipeline versions



Because 12 products are classified as Unknown, the brand-detection process should be improved.



Future versions could:



\* Use a dedicated brand field from a product-detail endpoint

\* Expand the recognised-brand dictionary

\* Standardise seller and manufacturer names

\* Manually review unidentified high-volume products

\* Apply text-matching rules to product titles



Improved brand identification would make competitor comparisons more accurate.



\### 6. Track prices over multiple extraction dates



The PostgreSQL fact table is designed to store repeated observations. The scheduled pipeline should continue collecting data so that future dashboards can show:



\* Price changes over time

\* Rating changes

\* Review growth

\* Product appearance and disappearance

\* Changes in Prime or sponsored status



Historical monitoring would provide stronger business intelligence than a single-date comparison.



\### 7. Investigate unusually expensive products



The scatter chart contains a product priced far above the majority of the market. Such outliers should be checked before making strategic decisions.



The retailer should confirm whether the product is:



\* A premium model

\* A bundle

\* An incorrectly classified listing

\* A marketplace pricing anomaly

\* A temporary seller price



\### 8. Avoid relying only on average values



The average price of €59.72 is useful, but the market includes both inexpensive and very expensive products. Decisions should also consider price-category distribution, brand-level results and individual product values.



\### 9. Differentiate beyond ratings



Since 31 of the 32 products are classified as Good or Excellent, ratings alone provide limited differentiation.



Retailers should emphasise:



\* Product design

\* Battery performance

\* Noise cancellation

\* Comfort

\* Microphone quality

\* Warranty

\* Sustainability

\* Delivery speed

\* Customer support



\### 10. Refresh the dashboard after every scheduled ETL run



Power BI should be refreshed after the scheduled Python pipeline loads new observations into PostgreSQL. This ensures decision-makers see the latest available competitor information.



\## Limitations



The analysis has several limitations:



1\. It contains a limited number of products from one Amazon Germany search query.

2\. API results may vary between extraction times.

3\. Twelve products could not be assigned to a recognised brand.

4\. Original prices and search positions were not available in the API response.

5\. Ratings and review counts are used as indicators of customer response, but they do not provide full sentiment information.

6\. The value score is a project-created exploratory metric and not an official Amazon measure.

7\. The dashboard represents marketplace observations and does not prove causal relationships.



\## Conclusion



The analysis shows a competitive wireless-headphones market dominated by affordable products with generally high ratings. JBL has broad product coverage, while Soundcore demonstrates particularly strong review activity. The dashboard also indicates that expensive products do not consistently achieve better ratings than affordable alternatives.



For retailers and category managers, the strongest opportunity is to combine competitive pricing with clear product differentiation and strong customer-review development. Continued scheduled data collection will make it possible to analyse historical price changes and improve future competitor-monitoring decisions.



