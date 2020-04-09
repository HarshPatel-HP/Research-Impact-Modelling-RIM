# -*- coding: utf-8 -*-
from scrapy import Spider
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from scrapy.selector import Selector
from scrapy.http import Request
from time import sleep
from selenium.common.exceptions import NoSuchElementException
import csv
from statistics import mean
import datetime

class GenericAuthorProfileScrapingSpider(Spider):
    # starting domain for GenericAuthorProfileScrapingSpider
    name = 'generic_author_profile_scraping'
    allowed_domains = ['scholar.google.ca']
    start_urls = ['http://scholar.google.ca/']
    list_start_urls = []
    # will open URL csv and read each URls one by None
    with open('C:\\Users\\Harsh\\RIM\\UofSherbrooke_Author_Profile_URLS.csv') as csvfile:
    	data_reader = csv.reader(csvfile, delimiter = ' ')
    	for row in data_reader:
    		list_start_urls.append(row[0])
    # will initiate ChromeDriverManager to open automated Chrome
    driver = webdriver.Chrome(ChromeDriverManager().install())
    i=0
    # we will here open csv in append mode to store all the
    #  scrped profile data for each authors
    with open('UofSherbrooke_BC_Author_Profiles_with_pub.csv','a',newline ='' , encoding = "utf-8") as csv_file:
        csv_columns = ['Author Name', 'Designation','Organization', 'Field', 'Citations', 'Citations Last Five Years',
        'h - index', 'h - index Last Five Years', 'i10 - index', 'i10 - index Last Five Years', 'Citation Count Year wise',
         'Co-Authos', 'Number_of_Publication', 'Years_Since_First_Pub_Year', 'Flag' ]
         # wrting data to csv file
        writer = csv.DictWriter(csv_file, fieldnames = csv_columns)
        writer.writeheader()

        # for each author we will  open it profile and then will scrape it.
        for i in range(len(list_start_urls)):
            driver.get(list_start_urls[i])
            next_rows = driver.find_element_by_xpath('//*[@id="gsc_bpf_more"]')
            while  next_rows.is_enabled():
                next_rows.click()
                sleep(3)

            # getting the source of the page
            sel = Selector(text = driver.page_source)
            # scrapte the author name
            author_name = sel.xpath("//*[@id = 'gsc_prf_in']/text()").extract_first()
            # scrape the designation of the author
            designation = sel.xpath("//*[@class = 'gsc_prf_il']/text()").extract_first()
            # scrape the organization of the author
            organization = sel.xpath("//*[@class = 'gsc_prf_il']/a/text()").extract_first()
            # scrape the filed of research of the author
            field = sel.xpath("//*[@id='gsc_prf_int']/a/text()").extract()
            # scrape the total citation of the author
            citation_total = sel.xpath("//table[@id='gsc_rsb_st']//td[2]/text()").extract_first()
            # scrape the total citation of the last five year
            citation_last_five = sel.xpath("//table[@id='gsc_rsb_st']//td[3]/text()").extract_first()
            # scrape the h-index of author
            h_index = sel.xpath("//*[@id='gsc_rsb_st']/tbody/tr[2]/td[2]/text()").extract_first()
            # scrape the h-index of last five years of authors
            h_index_last_five = sel.xpath("//*[@id='gsc_rsb_st']/tbody/tr[2]/td[3]/text()").extract_first()
            # scrape the i10-index of the author
            i_index = sel.xpath("//*[@id='gsc_rsb_st']/tbody/tr[3]/td[2]/text()").extract_first()
            # scrape the i10-index of last five years the author
            i_index_last_five = sel.xpath("//*[@id='gsc_rsb_st']/tbody/tr[3]/td[3]/text()").extract_first()
            # scrpae the total publciation of the author
            publications = sel.xpath("//*[@id='gsc_a_b']//a/text()").extract()
            # will scrape the author's publciation years
            author_pub_year = sel.xpath('//*[@class="gsc_g_t"]/text()').extract()
            author_pub_count_per_year = sel.xpath('//*[@class="gsc_g_al"]/text()').extract()
            # setting flag if any of the year in which author didnt received the citation
            if len(author_pub_year)==len(author_pub_count_per_year):
                flag = 0
            else:
                flag = 1
            # year wise citation count for authors
            year_wise_citation_count = [author_pub_year,author_pub_count_per_year]
            # scrae the co-authors details
            co_authors = sel.xpath('.//*[@class="gsc_rsb_a_desc"]/a/text()').extract()
            # will scrpe the publication Name
            pubs = sel.xpath("//*[@class = 'gsc_a_tr']")
            pub_counter =0
            Publication = {}
            pub_year_list=[]
            pub_title_list = []
            pub_citation_list = []
            # now to count years since first publcuation we have to find the
            # paper published in first year and then we will divide that
            # year from the 2020 current years
            for pub in pubs:
                pub_title = pub.xpath(".//*[@class = 'gsc_a_t']/a/text()").extract_first()
                citation_year = pub.xpath(".//*[@class = 'gsc_a_c']/a/text()").extract_first()
                pub_year = pub.xpath(".//*[@class = 'gsc_a_y']/span/text()").extract_first()
                pub_counter+=1
                pub_value_list = [citation_year,pub_year]
                pub_title_list.append(pub_title)
                pub_citation_list.append(pub_value_list)
                if pub_year is not None:
                    pub_year_list.append(int(pub_year))

            # Publication = dict(zip(pub_title_list,pub_citation_list))
            # if authors didnt received any citation then we will apoedn 2020 for
            # years sincce pub year counting
            if len(pub_year_list)!=0:
                First_Publication_Year = min(pub_year_list)
            else:
                First_Publication_Year = 2020

            x = datetime.datetime.now()
            current_year = x.year
            # counting the years since publications
            Years_Since_First_Pub_Year = current_year - First_Publication_Year
            if pub_counter <50:
                # sleep for scraping for 2 seconds
                sleep(2)
            # Appending all fetched data to file in form of dictionary
            mydict = {'Author Name': author_name, 'Designation': designation, 'Organization': organization, 'Field': field,
            'Citations': citation_total, 'Citations Last Five Years': citation_last_five, 'h - index': h_index,
            'h - index Last Five Years': h_index_last_five, 'i10 - index': i_index, 'i10 - index Last Five Years': i_index_last_five,
            'Citation Count Year wise': year_wise_citation_count, 'Co-Authos':co_authors,
            'Number_of_Publication': pub_counter,'Years_Since_First_Pub_Year': Years_Since_First_Pub_Year, 'Flag': flag}
            writer.writerow(mydict)

            print("--------------------------------")
            print(author_name)
            print("Total Publication: ",pub_counter)
            print("--------------------------------")
