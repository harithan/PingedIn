#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
__author__ = 'cognizac'
#
# Created:     14/02/2014
# Copyright:   (c) cognizac 2014
# Licence:     MIT
#-------------------------------------------------------------------------------

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from math import ceil
from time import sleep
from collections import OrderedDict
import numpy as np
import re


driver = webdriver.Firefox()
wait = WebDriverWait(driver, 10)

driver.get('https://www.linkedin.com')

username = driver.find_element_by_id('session_key-login')
password = driver.find_element_by_id('session_password-login')
submit_button = driver.find_element_by_id('login')

username.send_keys('YourEmailAddress')
password.send_keys('YourLinkedInPassword')
submit_button.submit()

#I'm going to look for tech recruiters in NYC.
# The open facets key G is used to set a Geographical Region, in my case NYC.
# Feel free to remove that and to set your own keywords.
driver.get('http://www.linkedin.com/vsearch/p?orig=FCTD&keywords=tech%20recruiter&openFacets=G,N,CC&f_G=us%3A70')

# How many results found?
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID,'results_count')))

#I prefer BS to do my scraping
soup = BeautifulSoup(driver.page_source, 'xml')

results_count = int(''.join([x for x in soup.find(attrs={'id':'results_count'}).p.text if x.isdigit()]))

#Let's be nice to LinkedIn and not hit their servers too hard. I'll keep a page retrieve count.
# So far I've opened two pages
page_view_count = 2

profiles_to_view = OrderedDict()

#loop to capture all results
for round in range(results_count):
    if not page_view_count < 500:
        #first visit 500 peoples pages before sleeping (keep total views at 1000)
        for page in OrderedDict(profiles_to_view):
            if page_view_count == 1000:
                break
            driver.get('https://www.linkedin.com'+profiles_to_view[page])
            profiles_to_view.pop(page)
            sleep(np.random.uniform(0, 5))
            page_view_count += 1

        #rest for a day
        sleep(60*60*24)
        #reset view counter
        page_view_count = 0

    people = soup.find(attrs={'id': 'results-container'}).findAll(attrs={'class':re.compile('mod result*')})
    for person in people:
        name = person.find(attrs={'class': 'title'}).text
        info = person.find(attrs={'class': 'description'}).text
        page_link = person.find(attrs={'class': 'title'})['href'] #investigate similar link as well
        profiles_to_view[name + ';' + info] = page_link

    print 'Pages stored: ' + str(len(profiles_to_view))

    #go to next page
    if round < 10 or len(profiles_to_view) <= 95: #ceil(results_count/10):
        sleep(np.random.uniform(0, 7))
        next_page = driver.find_element_by_class_name('next')
        next_page = WebDriverWait(next_page, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'page-link')))
        next_page.click()
        wait.until(EC.presence_of_element_located((By.ID, 'results-container')))
        soup = BeautifulSoup(driver.page_source, 'xml')
        # if soup.find(attrs={'class': 'hopscotch-bubble-close'}):
        #     close_button = wait.until(EC.presence_of_element_located((By.CLASS_NAME,'hopscotch-bubble-close')))
        #     close_button.click()
        #     wait.until(EC.presence_of_element_located((By.ID, 'results-container')))
        #     soup = BeautifulSoup(driver.page_source, 'xml')
    else:
        break


for page in OrderedDict(profiles_to_view):
    if page_view_count < 1000:
        driver.get('https://www.linkedin.com'+profiles_to_view[page])
        profiles_to_view.pop(page)
        sleep(np.random.uniform(0, 5))
        page_view_count += 1
    else:
        sleep(60*60*24)
        page_view_count = 0



