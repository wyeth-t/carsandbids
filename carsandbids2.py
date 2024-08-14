from google.cloud import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time 
import datetime
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
import pandas as pd
import traceback
import re


def convert_time(time_str):
    # Check if the string represents a number of days
    if 'day' in time_str.lower():
        # Extract the number of days
        days = int(re.search(r'\d+', time_str).group())
        # Convert the number of days to hours
        hours = days * 24
        # Return a time object with the hours
        duration = datetime.timedelta(hours=hours)
        return str(duration.total_seconds())
    else:
        # Split the string into hours, minutes, and seconds
        hours, minutes, seconds = map(int, time_str.split(':'))
        # Return a time object with the hours, minutes, and seconds
        duration = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
        return str(duration.total_seconds())

# Start virtual display
display = Display(visible=0, size=(800, 600))
display.start()

# Initialize a logger instance
client = logging.Client()
logger = client.logger("carsandbidslogger")

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
for _ in range(17):  # Adjust this value based on your needs
    driver.execute_script('window.scrollBy(0, 1000)')
    time.sleep(1)  # Wait for the page to load

html = driver.page_source
driver.quit()
display.stop()
soup = BeautifulSoup(html, "html.parser")
    
elements = soup.find_all("li", class_="auction-item")
carsandbids = pd.DataFrame(columns=['title', 'description', 'time_Left', 'bid', 'location', 'href', 'image_loc', 'timestamp'])

n = 1
timestamp = datetime.datetime.now()
timestamp = timestamp.strftime("%m/%d/%y %H:%M:%S")
for element in elements:
    try:
        element = BeautifulSoup(str(element), "html.parser")
        hero = element.find("li", class_="heroup")
        if hero is not None:
            continue
        try:
            #extract image location
            image_loc = element.find("img")['src']
        except:
            image_loc = 'No Image'
        try:
            #extract time left
            time_left = convert_time(element.find("li", class_="time-left").find("span", class_="value").text)
        except Exception as e:
            print("An error occurred:", str(e))
            time_left = '999999999999'
        #extract bid value
        try:
            bid = element.find("span", class_="bid-value").text
        except:
            bid = 'No Bid data'
        #extract the title, and link
        a_tag = element.find("div", class_="auction-title").find("a")
        try:
            title = a_tag.text
        except:
            title = 'No Title'
        try:
            href = adress[:-1] + str(a_tag['href'])
        except:
            href = 'No Href'
        try:
            #extract description
            description = element.find("p", class_="auction-subtitle").text
        except:
            description = 'No Description'
        try: 
            #extract location
            location = element.find("p", class_="auction-loc").text
        except:
            location = 'No Location'

        carsandbids.loc[len(carsandbids)] = [title, description, time_left, bid, location, href, image_loc, timestamp]

        n=n+1
            
    except Exception as e:
        print("An error occurred:", str(e))
        traceback.print_exc()
        print(n)
        n=n+1
        print(element)
        continue

print(carsandbids)
#if not carsandbids.empty:
    #logger.log_text('Cars and Bids data scraped successfully')

try:
    import mariadb
    import os
    
    conn = mariadb.connect(
        host=os.environ['DB_HOST'],
        port=int(os.environ['DB_PORT']),
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        database=os.environ['DB_NAME']
    )
    # Instantiate Cursor
    cursor = conn.cursor()

    # Drop the table if it already exists
    cursor.execute("DROP TABLE IF EXISTS carsandbids")

    # Create the table
    cursor.execute("""
        CREATE TABLE carsandbids (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255),
        description TEXT,
        time_Left VARCHAR(255),
        bid VARCHAR(255),
        location VARCHAR(255),
        href VARCHAR(255),
        image_loc VARCHAR(255),
        timestamp VARCHAR(255)
        )
        """)

    for index, row in carsandbids.iterrows():
        try:
            cursor.execute("""
                INSERT INTO carsandbids (title, description, time_Left, bid, location, href, image_loc, timestamp) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (row['title'], row['description'], row['time_Left'], row['bid'], row['location'], row['href'], row['image_loc'], row['timestamp']))
        except Exception as e:
            print(f"Error inserting row: {e}")

    conn.commit()  # Commit the transaction

    # Close Connection
    conn.close()
    
except Exception as e:
    print("An error occurred:", str(e))
    traceback.print_exc()