from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta
import os
import pyautogui
from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re

PAGE_LIMIT = 50
URL_FILE = "./URL.txt"

def announce(msg):
    os.system(f'say {msg}')
    print(msg)
    
def webScrap(DRIVER, URL):
    DRIVER.get(URL)
    html = DRIVER.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    if soup.title.text == "404 Not Found":
        print("Oops, seems like the URL formation went wrong")
        announce(msg="Error in getting the page")

    return soup

def getLastAuthorAndMsg(soup):
    outter_div = soup.find("div", {"class": "block-body js-replyNewMessageContainer"})
    if outter_div == None:
        print("Cannot retrive the message board")
        return None, None
    
    articles = outter_div.findChildren("article" , recursive=False)
    if len(articles) == 0:
        print("No messages in the message board")
        return None, None
    
    last_article = articles[-1]
    last_msg_ = last_article.find_all("div", {"class": "bbWrapper"})
    if len(last_msg_) != 0:
        last_msg_ = last_msg_[-1]
        removal_quotes = last_msg_.find_all('blockquote')
        for quotes in removal_quotes:
            quotes.decompose()
        
        return str(last_article["data-author"]), str(last_msg_.text.strip())
    else:
        print("Error in the last message")
        return None, None

def getNumber(DRIVER, URL):
    soup = webScrap(DRIVER, URL)
    return int(len(soup.find_all("article"))/2)

def getLastPageIndexFromURL(URL):
    return URL.index("page-")+5

def updateURL(original_url):
    return original_url[:getLastPageIndexFromURL(original_url)] + str(int(original_url[getLastPageIndexFromURL(original_url):]) + 1)

def findLastPoint(DRIVER, URL):
    start = getNumber(DRIVER, URL)
    while start == 50:
        URL = updateURL(URL)
        start = getNumber(DRIVER, URL)
    return start, URL
    
def readURL():
    with open(URL_FILE, 'r') as infile:
        url = infile.readline()
    infile.close()
    return url

if __name__ == '__main__':
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    DRIVER_MANAGER = ChromeDriverManager().install()
    DRIVER = webdriver.Chrome(service=Service(DRIVER_MANAGER), options=chrome_options)
    initial_url = readURL()
    url = initial_url + "page-1"

    last_time = datetime.now()
    last_num, url = findLastPoint(DRIVER, url)
    last_author, last_msg = getLastAuthorAndMsg(webScrap(DRIVER, url))
    if last_author == None or last_msg == None:
        print("Error retriving the last post")
    else:
        print("The last post was by " + last_author + " saying: " + last_msg)
     
    while True:
        new_num, url = findLastPoint(DRIVER, url)
        if new_num != last_num:
            announce(msg="There is a new post, number " + str((int(url[getLastPageIndexFromURL(url):])-1)*50 + new_num))
        else:
            diff = datetime.now() - last_time
            if diff > timedelta(minutes=60):
                print(last_time)
                announce("no difference in the last hour")
        last_time = datetime.now()
        last_num = new_num
        time.sleep(60)
        pyautogui.press("shift")
        