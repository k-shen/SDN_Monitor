from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta
import os
import pyautogui
from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

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
    last_article = soup.find_all("article")[-1]
    return str(last_article.blockquote["data-quote"]), str(last_article.find_all("div", {"class": "bbCodeBlock-expandContent js-expandContent"})[0].text.strip())

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
    DRIVER = webdriver.Chrome(DRIVER_MANAGER, options=chrome_options)
    initial_url = readURL()
    url = initial_url + "page-1"

    last_time = datetime.now()
    last_num, url = findLastPoint(DRIVER, url)
    last_author, last_msg = getLastAuthorAndMsg(webScrap(DRIVER, url))
    announce("The last post was by " + last_author + " saying: " + last_msg)
     
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
        