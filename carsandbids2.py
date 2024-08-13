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
for _ in range(17):  # Adjust this value based on your needs
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
        try:
            #extract image location
            image_loc = element.find("img")['src']
        except:
            image_loc = 'No Image'
        try:
            #extract time left
            time_left = element.find("li", class_="time-left").find("span", class_="value").text
        except:
            time_left = 'No Time left'
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

        carsandbids.loc[len(carsandbids)] = [title, description, time_left, bid, location, href, image_loc]

        n=n+1
            
    except Exception as e:
        print("An error occurred:", str(e))
        traceback.print_exc()
        print(n)
        n=n+1
        print(element)
        continue

    
print(carsandbids)
#logger.log_text(carsandbids.to_string())

try:
    import mariadb
    
    print('here')
    conn = mariadb.connect(
            host="34.41.191.0",
            port=3306,
            user="root",
            password='j"t~s?@qBDf#-Y-v',
            database='carsandbids')

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
        image_loc VARCHAR(255)
        )
        """)

    for index, row in carsandbids.iterrows():
        try:
            cursor.execute("""
                INSERT INTO carsandbids (title, description, time_Left, bid, location, href, image_loc) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (row['title'], row['description'], row['time_Left'], row['bid'], row['location'], row['href'], row['image_loc']))
        except Exception as e:
            print(f"Error inserting row: {e}")

    conn.commit()  # Commit the transaction

    # Close Connection
    conn.close()
    
except Exception as e:
    print("An error occurred:", str(e))
    traceback.print_exc()