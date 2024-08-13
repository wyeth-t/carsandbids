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
import traceback

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
#actions = ActionChains(driver)
for _ in range(15):  # Adjust this value based on your needs
    driver.execute_script('window.scrollBy(0, 1000)')
    time.sleep(1)  # Wait for the page to load

html = driver.page_source
driver.quit()
display.stop()
soup = BeautifulSoup(html, "html.parser")
    
elements = soup.find_all("li", class_="auction-item")
carsandbids = pd.DataFrame(columns=['title', 'description', 'time_Left', 'bid', 'location', 'href', 'image_loc'])

n = 1

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

        carsandbids.loc[len(carsandbids)] = [title, description, time_left, bid, location, href, image_loc]

        n=n+1
            
    except Exception as e:
        print("An error occurred:", str(e))
        traceback.print_exc()
        print(n)
        n=n+1

    
print(carsandbids)
logger.log_text(carsandbids.to_string())

try:
    from google.cloud.sql.connector import Connector
    import pymysql
    import sqlalchemy

    # initialize Connector object
    connector = Connector()

    # function to return the database connection
    def getconn() -> pymysql.connections.Connection:
        conn: pymysql.connections.Connection = connector.connect(
            "screenscrapper-431501:us-central1:screenscrapper2024",
            "pymysql",
            user="vm_user",
            password="dCB+b4lR|)J#nh@3",
            db="carsandbids"
        )
        return conn

    # create connection pool
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
     creator=getconn,
    )
except Exception as e:
        print("An error occurred:", str(e))
        traceback.print_exc()