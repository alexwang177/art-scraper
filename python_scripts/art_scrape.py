#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import hashlib
import io
import time
import os
import sys

sleep_between_interactions = 5


def accept_cookies():
    try:
        allow_cookies = wd.find_element_by_css_selector(
            "#onetrust-accept-btn-handler")
        allow_cookies.click()
    except Exception as e:
        pass


def close_signup():
    try:
        close_button = wd.find_element_by_css_selector(
            "#close_signup")
        close_button.click()
    except Exception as e:
        pass


def scrape_auction(wd, link):

    wd.get(link)
    time.sleep(3)


def scrape_auctions(wd, auction_links):

    for link in auction_links:
        scrape_auction(wd, link)
        time.sleep(1)


def scrape_christies():

    base_url = "https://www.christies.com/en/results?"

    for year in range(1998, 2022):
        for month in range(1, 13):
            wd.get(f"{base_url}month={month}&year={year}")

            accept_cookies()
            close_signup()

            try:
                _ = WebDriverWait(wd, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".chr-event-tile__title"))
                )

                auction_links = [e.get_attribute('href') for e in wd.find_elements_by_css_selector(
                    ".chr-event-tile__title")]

                scrape_auctions(wd, auction_links)

            except Exception as e:
                print(f"{e} for year {year} and month {month}")

            # time.sleep(sleep_between_interactions)


CHROMEDRIVER_PATH = "./drivers/chromedriver"
chrome_bin = os.environ.get("GOOGLE_CHROME_BIN", "chromedriver")
options = webdriver.ChromeOptions()
options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
wd = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,
                      options=options)

try:
    scrape_christies()
except Exception as e:
    print(e)

# wd.quit()
