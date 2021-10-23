#!/usr/bin/env python
from selenium import webdriver
from PIL import Image
import requests
import hashlib
import io
import time
import os
import sys

sleep_between_interactions = 1


def scrape_christies():

    base_url = "https://www.christies.com/en/results?"

    for year in range(1998, 2022):
        for month in range(1, 13):
            wd.get(f"{base_url}month={month}&year={year}")
            time.sleep(sleep_between_interactions)


CHROMEDRIVER_PATH = "./drivers/chromedriver"
chrome_bin = os.environ.get("GOOGLE_CHROME_BIN", "chromedriver")
options = webdriver.ChromeOptions()
options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
wd = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,
                      options=options)

try:
    scrape_christies()
except:
    print("load page error")

wd.quit()
