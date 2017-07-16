# News Crawler
News Crawler is created using Python Library 'Scrapy'.

* Functionality:
  * It crawles the news from URLs specified by end user at regular intervals of 15 minutes.
  * Crawled news items are inserted into Elastic Search Engine.
  * Crawled News can be visualized on Kibana Dashboard.

* Information provided by Kibana Dashboard:
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
