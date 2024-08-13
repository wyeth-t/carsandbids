from google.cloud import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time 
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
import pandas as pd

# Start virtual display
display = Display(visible=0, size=(800, 600))
display.start()

# Initialize a logger instance
client = logging.Client()
logger = client.logger("example_dot_com_logger")

# Setup WebDriver
webdriver_service = Service(ChromeDriverManager().install())
chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
adress = "https://carsandbids.com/"
driver.get(adress)

time.sleep(10)

# Scroll down
actions = ActionChains(driver)
for _ in range(15):  # Adjust this value based on your needs
    actions.send_keys(Keys.PAGE_DOWN).perform()
    time.sleep(1)  # Wait for the page to load

html = driver.page_source
driver.quit()
display.stop()
soup = BeautifulSoup(html, "html.parser")
    
elements = soup.find_all("li", class_="auction-item")
carsandbids = pd.DataFrame(columns=['title', 'description', 'time_Left', 'bid', 'location', 'href', 'image_loc'])

n = 1
print(len(elements))
print(elements[10])
for element in elements:
    try:
        element = BeautifulSoup(str(element), "html.parser")
        hero = element.find("li", class_="heroup")
        if hero is not None:
            continue
        image_loc = element.find("img")['src']
        time_left = element.find("li", class_="time-left").find("span", class_="value").text
        #extract bid value
        bid = element.find("span", class_="bid-value").text
        #extract the title, and link
        a_tag = element.find("div", class_="auction-title").find("a")
        title = a_tag.text
        href = adress[:-1] + str(a_tag['href'])
        #extract description
        description = element.find("p", class_="auction-subtitle").text
        #extract location
        location = element.find("p", class_="auction-loc").text

        my_list = [title, description, time_left, bid, location, href, image_loc]
        new_row = pd.Series(my_list, index=carsandbids.columns)
        carsandbids = carsandbids.append(new_row, ignore_index=True)
            
    except Exception:
        continue

    
print(carsandbids)
logger.log_text(carsandbids.to_string())

