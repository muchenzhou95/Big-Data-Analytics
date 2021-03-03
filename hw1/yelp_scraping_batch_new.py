import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re
import numpy as np
import csv
import pandas as pd 
import os.path
from os import path

PROXY = 'http://yourproxyhere:@proxy.crawlera.com:8010/'
MY_HEADERS = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}


#with open('urls.csv', newline='') as f:
#    reader = csv.reader(f)
#    URLS = list(reader)

#URLS = URLS[1:]

TESTING_HANDLE = 'https://www.yelp.com/biz/daigo-handroll-bar-brooklyn?osq=sushi&sort_by=date_desc'
def set_driver():
    proxy = PROXY
    webdriver.DesiredCapabilities.CHROME['proxy'] = {
        "httpProxy":proxy,
        "ftpProxy":proxy,
        "sslProxy":proxy,
        "proxyType":"MANUAL",
    }    
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) ' \
        'Chrome/80.0.3987.132 Safari/537.36'
    chrome_option = webdriver.ChromeOptions()
    chrome_option.add_argument('--no-sandbox')
    chrome_option.add_argument('--disable-dev-shm-usage')
    chrome_option.add_argument('--ignore-certificate-errors')
    chrome_option.add_argument("--disable-blink-features=AutomationControlled")
    chrome_option.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) ' \
        'Chrome/80.0.3987.132 Safari/537.36')
    chrome_option.add_argument('--proxy-server=%s' % PROXY)
    chrome_option.headless = True

    driver = webdriver.Chrome(options = chrome_option)
    return driver

def find_restaurant_metadata(url):
    driver = set_driver()
    for j in range(1,6): 
        try:
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, 'lxml')
            driver.quit()
            break 
                # if requests.get() threw an exception, i.e., the attempt to get the response failed
        except:
            print ('failed attempt #',i)
            # wait 2 secs before trying again
            time.sleep(2)
    if len(soup)>0:
        restaurant_title = soup.find('h1').text
        restaurant_reviews = soup.find('span',{'class':re.compile('lemon--span__373c0__3997G text__373c0__2Kxyz text-color--white__373c0__22aE8 text-align--left__373c0__2XGa- text-weight--semibold__373c0__2l0fe text-size--large__373c0__3t60B')}).text.split()[0]
        #temp = soup.find('div', {'class':re.compile('lemon--div__373c0__1mboc pagination__373c0__3z4d_ border--top__373c0__3gXLy border--bottom__373c0__3qNtD border-color--default__373c0__3-ifU')})
        restaurant_pages = soup.findAll('div', {'class':re.compile('lemon--div__373c0__1mboc border-color--default__373c0__3-ifU text-align--center__373c0__2n2yQ')})[-1].text.split()[2]
        restaurant_rating = soup.findAll('div', {'class':re.compile('lemon--div__373c0__1mboc arrange-unit__373c0__o3tjT border-color--default__373c0__3-ifU')})[2].find('div')['aria-label'].split()[0]
        try: 
            restaurant_pricelevel = len(soup.find('span', {'class':re.compile('lemon--span__373c0__3997G text__373c0__2Kxyz text-color--white__373c0__22aE8 text-align--left__373c0__2XGa- text-weight--semibold__373c0__2l0fe text-bullet--after__373c0__3fS1Z text-size--large__373c0__3t60B')}).text.strip())
            restaurant_types = soup.findAll('span', {'class':re.compile('lemon--span__373c0__3997G display--inline__373c0__3JqBP margin-r1__373c0__zyKmV border-color--default__373c0__3-ifU')})[2].find_all('a')        
        except:
            restaurant_pricelevel = -1
            restaurant_types = soup.findAll('span', {'class':re.compile('lemon--span__373c0__3997G display--inline__373c0__3JqBP margin-r1__373c0__zyKmV border-color--default__373c0__3-ifU')})[1].find_all('a')        
        restaurant_type = []
        restaurant_secondary_type = ''
        restaurant_thirdary_type = ''
        for i in range (0,len(restaurant_types)):
            restaurant_type.append(restaurant_types[i].text)
        restaurant_primary_type = restaurant_type[0]
        if len(restaurant_types)>=2:
            restaurant_secondary_type = restaurant_type[1]
            if len(restaurant_types)>=3:
                restaurant_thirdary_type = restaurant_type[2]
        #print (soup.find('address').find_all('span'))
        restaurant_streets = soup.find('address').find_all('span')[0].text
        restaurant_city = soup.find('address').find_all('span')[-1].text.split(',')[0]
        restaurant_state = soup.find('address').find_all('span')[-1].text.split(',')[1].split()[0]
        restaurant_zipcode= soup.find('address').find_all('span')[-1].text.split(',')[1].split()[1]
        metadata = pd.DataFrame(data = {'restaurant_url' : url,
                                        'restaurant_title' : restaurant_title,
                                        'restaurant_rating' : restaurant_rating,
                                        'restaurant_reviews_count': restaurant_reviews,
                                        'restaurant_reviews_pages': restaurant_pages,
                                        'restaurant_pricelevel': restaurant_pricelevel,
                                        'restaurant_primary_type' : restaurant_primary_type,
                                        'restaurant_secondary_type' : restaurant_secondary_type,
                                        'restaurant_thirdary_type' : restaurant_thirdary_type,
                                        'restaurant_streets' : restaurant_streets,
                                        'restaurant_city' : restaurant_city,
                                        'restaurant_state' : restaurant_state,
                                        'restaurant_zipcode' : restaurant_zipcode},index=[0])
                                        #,
                                        #'recommendations_list' : recommendations_list})
        print ('Metadata Done!')
        return metadata 


def parse_reviewer(userid,dummy = 0):
    if dummy == 0:
        return [0,0,0,0,0,0]
    else:
        #print ('Getting User' + str(userid))
        #driver = set_driver()
        url = 'https://www.yelp.com' + userid
        for j in range(1,6): 
            try:
                response = requests.get(url, headers = MY_HEADERS,proxies={"http":PROXY,"https":PROXY,})
                restaurant_response = BeautifulSoup(response.content.decode('ascii', 'ignore'), 'lxml')
                break 
            # if requests.get() threw an exception, i.e., the attempt to get the response failed
            except:
                print ('failed attempt #',j)
                # wait 2 secs before trying again
                time.sleep(2)

        #restaurant_response.findAll('td', {'class':re.compile('histogram_count')})        
        result_list = [int(ct.text) for ct in restaurant_response.find_all('td', {'class':re.compile('histogram_count')})]
        if len(result_list) != 5:
            return [0,0,0,0,0,1]
        else:
            result_list.append(1)
            return result_list



def find_reviews(url,counter):
    driver = set_driver()
    for j in range(1,6): 
        try:
            driver.get(url)
            restaurant_response = BeautifulSoup(driver.page_source, 'lxml')
            driver.quit()
            break 
        # if requests.get() threw an exception, i.e., the attempt to get the response failed
        except:
            print ('failed attempt #',i)
            # wait 2 secs before trying again
            time.sleep(2)

    df = pd.DataFrame()
    #sections = restaurant_response.findAll('div', {'class':re.compile('lemon--div__373c0__1mboc review__373c0__13kpL sidebarActionsHoverTarget__373c0__2kfhE arrange__373c0__2C9bH gutter-2__373c0__1DiLQ grid__373c0__1Pz7f layout-stack-small__373c0__27wVp border-color--default__373c0__3-ifU')})
    sections = restaurant_response.findAll('div', {'class':re.compile('lemon--div__373c0__1mboc review__373c0__13kpL border-color--default__373c0__3-ifU')})
    #print (len(sections))
    #print (len(sections))
    for section in sections:
        reviews_df = dict()
        reviews_df['counter'] = counter 
        counter += 1
        reviewer_elite = 'Not A Yelp Elite'
        review_photos = 0
        review_useful = 0
        review_funny = 0 
        review_cool = 0
        span = section.findAll('span')
        # reviewer_name
        reviewer_name = span[0].find('a').text.split()[0]
        reviews_df['reviewer_name'] = reviewer_name
        # reviewer userid
        reviewer_userid = span[0].find('a')['href']
        reviews_df['reviewer_userid'] = reviewer_userid
        # reviewer location
        reviewer_city = np.nan
        reviewer_state = np.nan
        if len(span[1].text) > 0:
            if len(span[1].text.split(',')) == 2:
                reviewer_city = span[1].text.split(',')[0]
                reviewer_state = span[1].text.split(',')[1]
            elif len(span[1].text.split(',')) == 3:
                reviewer_city = span[1].text.split(',')[1]
                reviewer_state = span[1].text.split(',')[2]
        reviews_df['reviewer_city'] = reviewer_city
        reviews_df['reviewer_state'] = reviewer_state
        #reviewer_elite
        elite_bar = section.find('p').find('a')
        if elite_bar:
            reviewer_elite = elite_bar.text
        reviews_df['reviewer_elite'] = reviewer_elite
        # review rating
        review_rating = section.find('div', {'class':re.compile('lemon--div__373c0__1mboc i-stars__373c0__1T6rz i-stars--regular')})["aria-label"].split()[0]
        reviews_df['review_rating'] = review_rating
        # review date
        review_date = section.findAll('span',{'class':'lemon--span__373c0__3997G text__373c0__2Kxyz text-color--mid__373c0__jCeOG text-align--left__373c0__2XGa-'})[0].text
        reviews_df['review_date'] = review_date
        # review photos
        a = section.find('div',{'class':re.compile('lemon--div__373c0__1mboc margin-b2__373c0__abANL border-color--default__373c0__3-ifU')}).find('a')
        if a:
            try: 
                review_photos = a.text.split()[0]
            except:
                review_photos = 0
        reviews_df['review_photos'] = review_photos
        #review_content
        review_content = section.find('span',{'class':re.compile('lemon--span__373c0__3997G raw__373c0__3rcx7')}).text
        reviews_df['review_content'] = review_content
        #review_mood
        review_moods = section.findAll('span',{'class':re.compile('lemon--span__373c0__3997G text__373c0__2Kxyz text-color--black-extra-light__373c0__2OyzO text-align--left__373c0__2XGa- text-size--small__373c0__3NVWO')})
        if len(review_moods[0]) == 2:
            review_useful = review_moods[0].text.split()[1]
        if len(review_moods[1]) == 2:
            review_funny = review_moods[1].text.split()[1]
        if len(review_moods[2]) == 2:
            review_cool =  review_moods[2].text.split()[1]
        reviews_df['review_useful'] = review_useful
        reviews_df['review_funny'] = review_funny
        reviews_df['review_cool'] = review_cool
        if counter <= 100:
            reviewer_list = parse_reviewer(reviewer_userid,dummy = 1)
            time.sleep(2)
        else:
            reviewer_list = parse_reviewer(reviewer_userid,dummy = 0)
        reviews_df['reviewer_fivestars'] = reviewer_list[0]
        reviews_df['reviewer_fourstars'] = reviewer_list[1]
        reviews_df['reviewer_threestars'] = reviewer_list[2]
        reviews_df['reviewer_twostars'] = reviewer_list[3]
        reviews_df['reviewer_onestar'] = reviewer_list[4]
        reviews_df['reviewer_scraped_flag'] = reviewer_list[5]
        df = df.append(reviews_df,ignore_index = True)
    #print ('Review Page Done!')
    #print (df)
    return df 




def scrape_restaurant(url,number_restaurants):
    #scrape metadata
    for i in range(3):
        try:
            restaurant_metadata = find_restaurant_metadata(url)
            #restaurant_metadata.to_csv('restaurant_metadata_{}.csv'.format(number_restaurants),index=False)
            break
        except:
            print ('=============DIDNT RUN===============')
    if len(restaurant_metadata)>0:
        reviews_page = int(restaurant_metadata['restaurant_reviews_pages'])
        #print (reviews_page)
        #scrape reviews 
        counter = 0
        reviews_df = find_reviews(url,counter)
        if reviews_page > 1:
            for i in range(1,reviews_page - 1):
                print ('scraping page {}'.format(i))
                reviews = find_reviews(url+'?start={}&sort_by=date_desc'.format(20*i),20*i)
                while len(reviews) == 0: 
                    reviews = find_reviews(url+'?start={}&sort_by=date_desc'.format(20*i),20*i)
                reviews_df = reviews_df.append(reviews)
        reviews_df.to_csv('{}.csv'.format(number_restaurants),index=False)
        print ('URL: {} done'.format(url))
    else:
        print ('====================URL: {} NOT done===================='.format(url))

#scrape_restaurant(TESTING_HANDLE)

def batch_scrape(starting_number,number_restaurants):
    url_df = pd.read_csv('clean_urls.csv')
    for i in range(starting_number,starting_number+number_restaurants):
        url = url_df['urls'][i]
        print ('{}.csv'.format(i))
        if path.exists('{}.csv'.format(i)) == False:
            print ('URL: {} starts!'.format(url))
            #for i in range(1,1):
                #try:
            scrape_restaurant(url,i)
                #break
                #except:
                #    print ('There was something wrong with page: {}'.format(url))
        time.sleep(3)



#batch_scrape(300,300)
print ('done')