# News Crawler
News Crawler is created using Python Library 'Scrapy'.

## Functionality:
  * It crawles the news from URLs specified by end user at regular intervals of 15 minutes.
  * Crawled news items are inserted into Elastic Search Engine.
  * Crawled News can be visualized on Kibana Dashboard.

## Installation and Usage:
  * Please refer README.pdf
  
## Information provided by Kibana Dashboard:
  * Total news feeds fetched.
  * Time Duration for which news items exist in Elastic Search.
  * Distribution of News Items by Location:
    * News Items are displayed on world map, based on countries specifed in News.
  * Distribution of News Items by Source:
    * News Source is the website from which the news is fetched.
    * For Example: BBC, CNN, New York Times etc.
  * Distribution of News Item by Category:
    * For Example: World, Top Stories, Sports, Science, Technology etc. 
  * Countries mentioned recently in News:
    * Top 20 countries recently mentioned in news.
  * Latest News Headlines
  
 ## Kibana Dashboard View
 
![dashboard_view_1](https://user-images.githubusercontent.com/14314997/28247540-2280448e-6a50-11e7-8c44-2a84fd5bfe46.png)
![dashboard_view_2](https://user-images.githubusercontent.com/14314997/28247541-2619df42-6a50-11e7-94d1-56723d3c2c1a.png)
