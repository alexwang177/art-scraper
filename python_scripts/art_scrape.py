#!/usr/bin/env python
from selenium import webdriver
from PIL import Image
import requests
import hashlib
import io
import time
import os
import sys


def scrape_christies():
    # load the page
    wd.get("https://www.christies.com/en/results")


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
