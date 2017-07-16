"""
Created on Mon July 10, 2017

@author: Ruchika Chhabra
"""
import scrapy
import csv
import time
import os
import requests
import json
import sys
import geograpy
from   configReader import ConfigParse
from   selenium import webdriver
from   geopy.geocoders import Nominatim
from   datetime import datetime
from   elasticsearch import Elasticsearch

def get_urls_from_csv(urlFile):
    '''
    DESCRIPTION:
    ------------
    This function reads the URLs, to be scraped from the csv provided by end user.

    PARAMETERS:
    ----------
    1. urlFile: CSV file name containing list of  URLS to be scraped.

    RETURNS:
    --------
    1. scrapUrls   : List of URLs to be scraped.
    2. categoryDict: Dictionary with news category as 'key' and list of
                     news urls as 'value'.
    '''
    with open(urlFile, 'rb') as csv_file:
        data = csv.reader(csv_file)
        scrapUrls = []
        categoryDict = {}
        for row in data:
            scrapUrls.append(row[1].strip())
            if row[0] in categoryDict.keys():
                categoryDict[row[0]].append(row[1].strip())
            else:
                categoryDict[row[0]] = [row[1].strip()]
    return (scrapUrls, categoryDict)

class NewsCrawlerSpider(scrapy.Spider):
    '''
    DESCRIPTION:
    ------------
    This class implements News Crawler using
    Spider class of Scrapy.

    PARAMETERS:
    ----------
    1. scrapy.Spider: Class of Scrapy which is inherited
                      to implement News Crawler.
    '''
    name                          = 'newsCrawler'
    configParser = ConfigParse()
    configParser.configReader()
    (start_urls, urlCategoryDict) = get_urls_from_csv(configParser.URL_File)

    def __init__(self):
        '''
        DESCRIPTION:
        -----------
        This function initializes attributes of News Crawler Class.
        '''
        scrapy.Spider.__init__(self)

        # initialize ES engine
        self.initializeES()

        self.parseURL = True

        # use any browser you wish
        self.browser    = webdriver.Firefox()
        print "Please don't close Firefox browser, it will be closed automatically!"
        self.dateFormat = '%B %d, %Y, %I:%M %p'

        # Initialize maxTimeStamp and timeStamp for each News Category
        self.maxTimeStamp = {}
        self.timeStamp    = {}
        for newsCategory in NewsCrawlerSpider.urlCategoryDict.keys():
            self.maxTimeStamp[newsCategory]   = None
            # Read timestamp from files
            if os.path.exists('TimeStamp/' + newsCategory + '.stamp'):
                infile = open('TimeStamp/' + newsCategory + '.stamp', 'r')
                self.timeStamp[newsCategory] = datetime.strptime(infile.readline(), '%Y-%m-%d %H:%M:%S')
            else:
                self.timeStamp[newsCategory] = None

    def initializeES(self):
        '''
        DESCRIPTION:
        ------------
        This function initializes the ES engine.
        '''
        # Connect to ElasticSearch Engine
        # Make sure Elastic is up and running
        try:
            elasticServerRes = requests.get('http://' + NewsCrawlerSpider.configParser.ES_Host + \
                                            ':' + str(NewsCrawlerSpider.configParser.ES_Port))
        except:
            print("Error: ElasticSearch Server not up and running!")
            sys.exit(1)

        # connect to our cluster
        self.es = Elasticsearch([{'host': NewsCrawlerSpider.configParser.ES_Host, \
                                  'port': NewsCrawlerSpider.configParser.ES_Port}])

        # Delete the existing index (with given name) from ES
        if (NewsCrawlerSpider.configParser.del_flag):
            self.es.indices.delete(index=NewsCrawlerSpider.configParser.Index_Name, ignore=[400, 404])
        # create the ES index (with given name)
        self.es.indices.create(index=NewsCrawlerSpider.configParser.Index_Name, \
                               body=json.load(open(NewsCrawlerSpider.configParser.Mapping_File)), ignore=400)
        self.ESdocID = NewsCrawlerSpider.configParser.Index_ID + 1

    def isLatestNews(self, category, pubDate):
        '''
        DESCRIPTION:
        ----------
        * This function determines, whether the crawled news is news or not.
          By comparing the publish date of crawled news, with the timestamp
          already stored for each news category.
        * "timestamp" stores the published time of last news inserted into ES,
          for each news category.

        PARAMETERS:
        -----------
        1. category: Category of crawled news.
        2. pubDate:  Publish date of crawled news.

        RETURNS:
        -------
        'True' if pubDate of crawled news is greater than last news item stored in
        ES for the same news category, Otherwise returns 'False'.
        '''
        if (category in NewsCrawlerSpider.urlCategoryDict.keys()):
            timestamp = self.timeStamp[category]
        else:
            timestamp = None

        if (timestamp == None or  timestamp < datetime.strptime(pubDate, self.dateFormat)):
            return True
        return False

    def updateMaxTimeStamp(self, category, pubDate):
        '''
        DESCRIPTION:
        ------------
        * This function is called after every news item is crawled.
        * It sets maxTimeStamp for the news category received as argument.
        * 'maxTimeStamp' is used to update 'timeStamp' for each news Category,
          once a URL has been crawled.

        PARAMETERS:
        -----------
        1. category: News Category for which Max Time Stamp is to be updated.
        2. pubDate : pubDate of crawled News.
        '''
        if (category in NewsCrawlerSpider.urlCategoryDict.keys() and
            (self.maxTimeStamp[category] == None or self.maxTimeStamp[category] < \
            datetime.strptime(pubDate, self.dateFormat))):
            self.maxTimeStamp[category] = datetime.strptime(pubDate, self.dateFormat)

    def updateTimestamp(self):
        '''
        DESCRIPTION:
        ------------
        * This function is called once a URL has been crawled.
        * It updates the timestamp of each news category with maxTimeStamp.
        '''
        for newsCategory in NewsCrawlerSpider.urlCategoryDict.keys():
            if self.maxTimeStamp[newsCategory] != None:
                stampFile = open('TimeStamp/' + newsCategory +'.stamp', 'w+')
                stampFile.write(str(self.maxTimeStamp[newsCategory]))
                stampFile.close()

    def getNewsCategory(self, urlString):
        '''
        DESCRIPTION:
        -----------
        This function finds the News Category corresponding to URL.

        PARAMETERS:
        ----------
        1. urlString: URL corresponding to which News Category is to be found.

        RETURNS:
        --------
        News Category of URL received as argument.
        '''
        for newsCategory in NewsCrawlerSpider.urlCategoryDict.keys():
            if urlString in NewsCrawlerSpider.urlCategoryDict[newsCategory]:
                return newsCategory
        return 'UnknownCategory'

    def insertToES(self, newsItem):
        '''
        DESCRIPTION:
        -----------
        This function inserts crawled newsItem into ES.

        PARAMETERS:
        -----------
        1. newsItem: Crawled News data to be inserted to ES.
        '''
        try:
            self.es.index(index='news', doc_type='news_type', id=self.ESdocID, body=newsItem)
            self.ESdocID += 1
        except:
            return (-1)

    def getNewsSource(self, url):
        '''
        DESCRIPTION:
        -----------
        This function is responsible for extracting the news source from news url.

        PARAMETERS:
        ----------
        1. url: News URL from which news source is extracted.

        RETURNS:
        -------
        This function returns News source of News URL received as argument.
        '''
        start = url.find('//')
        if (start != -1):
            source = url[(start + 2):]
        else:
            source = url
        end    = source.find('/')
        if (end != -1):
            source = source[:end]
        return source

    def getGeoLocation(self, newsUrl):
        '''
        DESCRIPTION:
        ------------
        This function finds the country and it's geo location, specified
        in newsurl.

        PARAMETERS:
        -----------
        newsurl: URL corresponding to news.

        RETURNS:
        --------
        1. geoPoint: Lat Long of country mentioned in newsUrl.
        2. country : Country specified in newsUrl.
        '''
        # Set the geo_point
        places    = geograpy.get_place_context(url = newsUrl)
        geoPoint  = []
        country   = ""
        try:
            for country in places.country_mentions:
                country    = country[0].encode('ascii', 'ignore')
                geolocator = Nominatim()
                location   = geolocator.geocode(country)
                geoPoint.append(location.longitude)
                geoPoint.append(location.latitude)
                break
        except:
            geoPoint = []
            country  = ""
        return (geoPoint, country)

    def parse(self, response):
        '''
        DESCRIPTION:
        -----------
        This function parses all the URLS, fetch and store all the required data.
        '''
        if (self.parseURL == True):
            print 'Crawling URL: ' + str(response.url)
            try :
                self.browser.get(response.url)
                # let JavaScript Load
                time.sleep(5)

                # scrape dynamically generated HTML
                hxs = scrapy.Selector(text=self.browser.page_source)

                newsBlock    = hxs.xpath('//div[@id="feedContent"]')
                for news in newsBlock.xpath('.//div[@class="entry"]'):
                    category = self.getNewsCategory(response.url)
                    pubDate  = news.xpath('.//h3/div[@class="lastUpdated"]/text()').extract()
                    # Check if the news is latest
                    if pubDate and self.isLatestNews(category, pubDate[0]):
                        newsItem = dict()
                        newsItem['category']    = category.encode('ascii', 'ignore')
                        title                   = news.xpath('.//h3/a/span/text()').extract()
                        if title:
                            newsItem['title']   = title[0].encode('ascii', 'ignore')
                        description             = news.xpath('.//div[@class="feedEntryContent"]/text()').extract()
                        if description:
                            newsItem['description'] = description[0].encode('ascii','ignore')
                        link                      = news.xpath('.//h3/a/@href').extract()
                        if link:
                            newsItem['link']      = link[0].encode('ascii', 'ignore')
                            # Set the geoPoint and Country
                            newsItem['geo_point'], newsItem['country'] = self.getGeoLocation(newsItem['link'])
                            # Set the news source
                            newsItem['source'] = self.getNewsSource(response.url)
                        if pubDate:
                            dateTime = pubDate[0].encode('ascii','ignore').split(',')
                            date = ','.join(dateTime[:len(dateTime) - 1])
                            newsItem['pubDate'] = datetime.strptime(date, '%B %d, %Y').date()
                            self.updateMaxTimeStamp(category, pubDate[0])

                        mediaFilePath = news.xpath('.//div[@class="enclosures"]/div[@class="enclosure"]/a/@href').extract()
                        if mediaFilePath:
                            newsItem['mediaFiles'] = (mediaFilePath[0].encode('ascii', 'ignore'))
                        if (self.insertToES(newsItem) == -1):
                            self.parseURL = False
            except:
                pass
            self.updateTimestamp()

    def close(self, reason):
        '''
        DESCRIPTION:
        ------------
        This function is called once all the URLs have been crawled.
        In this function browser used for crawling is closed.
        '''
        self.configParser.updateConfigParam('delete_index', 0)
        self.configParser.updateConfigParam('index_id', self.ESdocID)
        self.browser.close()