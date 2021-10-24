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


def scrape_auction(wd, link, keyword_dict):
    wd.get(link)

    asian_piece_count = 0

    try:
        _ = WebDriverWait(wd, 3).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".chr-auction-header__auction-title"))
        )

        auction_title = wd.find_element_by_css_selector(
            ".chr-auction-header__auction-title").text.lower()

        print(f"\nAuction Title: {auction_title}")

        # _ = WebDriverWait(wd, 3).until(
        #     EC.presence_of_element_located(
        #         (By.CSS_SELECTOR, ".chr-lot-tile__link"))
        # )

        piece_titles = [e.text.lower() for e in wd.find_elements_by_css_selector(
            ".chr-lot-tile__link")]

        super_keyword_set = set()

        for keyword in keyword_dict:

            if keyword in auction_title:

                keyword_dict[keyword] += len(piece_titles)
                super_keyword_set.add(keyword)
                print("SPECIAL!!!")

        for title in piece_titles:

            match = False

            for keyword in keyword_dict:

                if keyword in super_keyword_set:
                    continue

                if keyword in title:
                    match = True
                    keyword_dict[keyword] += 1

            if match:
                asian_piece_count += 1

    except Exception as e:
        print(e)

    return asian_piece_count


def scrape_auctions(wd, auction_links, keyword_dict):

    asian_piece_count = 0

    for link in auction_links:

        accept_cookies()
        close_signup()

        asian_piece_count += scrape_auction(wd, link, keyword_dict)
        print(keyword_dict)

    return asian_piece_count


def scrape_christies(year):
    keyword_dict = {"chinese": 0,
                    "china": 0,
                    "korean": 0,
                    "korea": 0,
                    "japanese": 0,
                    "japan": 0,
                    "orient": 0,
                    "dynasty": 0,
                    "asian": 0,
                    "asia": 0}
    asian_piece_count = 0

    base_url = "https://www.christies.com/en/results?"

    for month in range(1, 13):

        print(F"\nMONTH {month}\n")

        wd.get(f"{base_url}month={month}&year={year}")

        accept_cookies()
        close_signup()

        try:
            _ = WebDriverWait(wd, 5).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".chr-event-tile__title"))
            )

            auction_links = [e.get_attribute('href') for e in wd.find_elements_by_css_selector(
                ".chr-event-tile__title")]

            asian_piece_count += scrape_auctions(wd,
                                                 auction_links, keyword_dict)

            print(asian_piece_count)
            print(keyword_dict)

        except Exception as e:
            print(f"{e} for year {year} and month {month}")


CHROMEDRIVER_PATH = "./drivers/chromedriver"
chrome_bin = os.environ.get("GOOGLE_CHROME_BIN", "chromedriver")
options = webdriver.ChromeOptions()
options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
wd = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,
                      options=options)

try:
    scrape_christies(sys.argv[1])
except Exception as e:
    print(e)

wd.quit()
