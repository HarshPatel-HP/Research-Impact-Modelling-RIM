# -*- coding: utf-8 -*-
from scrapy import Spider
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from scrapy.selector import Selector
from scrapy.http import Request
from time import sleep
from selenium.common.exceptions import NoSuchElementException

# initiating Spider
class AuthorProfileUrlsSpider(Spider):
    # Defining the starting URL
    name = 'author_profile_urls'
    allowed_domains = ['scholar.google.ca']
    # satarting the ChromeDriverManager for scraping using selenium
    def start_requests(self):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.get('https://scholar.google.ca/citations?view_op=view_org&org=7596114524987823391&hl=en&oi=io')
        # storing the targeted page spurce
        sel = Selector(text = self.driver.page_source)
        authors = sel.xpath('//*[@class="gsc_1usr"]')
        # searching for author and foreach author we will scrape the URL
        for author in authors:
            author_url = author.xpath('.//*[@class="gs_ai_name"]/a/@href').extract_first()
            url = 'https://scholar.google.ca/' + author_url
            # will open the author page to scrape the URL
            yield Request(url, callback = self.parse)

        while True:
            try:
                # asking crawler to crawl for more pages
                next_page = self.driver.find_element_by_xpath('//*[@id="gsc_authors_bottom_pag"]/div/button[2]')
                # crawler will go in sleep for 3 seconds to maintain the web scraping ethics
                sleep(3)
                self.logger.info("Sleeping for 3 seconds!!")
                next_page.click()
                # for the each craled next page we will crawl the data
                sel = Selector(text = self.driver.page_source)
                authors = sel.xpath('//*[@class="gsc_1usr"]')
                # for all crawled next page we will scrape the URls
                for author in authors:
                    author_url = author.xpath('.//*[@class="gs_ai_name"]/a/@href').extract_first()
                    url = 'https://scholar.google.ca/' + author_url
                    yield Request(url, callback = self.parse)
            except NoSuchElementException:
                self.logger.info("No more pages to load")
                self.driver.quit()
                break

    def parse(self, response):
        # return author url
        url = response.request.url
        yield {'URls': url}
