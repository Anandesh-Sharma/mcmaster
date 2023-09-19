import time 
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
import undetected_chromedriver as uc
from loguru import logger
from xpath import *

# Initialize the Chrome WebDriver
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Optional: Run Selenium in headless mode

# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver = uc.Chrome(headless=False, use_subprocess=True)

# Set a maximum wait time (in seconds)
max_wait_time = 10
wait = WebDriverWait(driver, max_wait_time)


"""Get the main categories"""
try:
    # Navigate to the website
    driver.get("https://mcmaster.com")
    time.sleep(10)
    try:
        driver.find_element(By.XPATH, '//*[@id="Email"]').send_keys('anandeshsharma@gmail.com')
        driver.find_element(By.XPATH, '//*[@id="Password"]').send_keys('Rock0004@')
        driver.find_element(By.XPATH, '//input[@value="Log in"]').click()
    except NoSuchElementException:
        logger.info('Skipping logging in')

    categories = driver.find_elements(By.XPATH, CATEGORIES)
    print(categories)

    time.sleep(100)

finally:
    # Close the WebDriver when done
    driver.quit()
