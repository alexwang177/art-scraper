#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
import hashlib
import io
import time
import os
import sys
import csv


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


def scroll_to_bottom(wd):
    wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")


def wait_for_elements(wait):
    try:
        wait.until(
            lambda wd:
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".chr-auction-header__auction-title")) and
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, ".chr-lot-tile__link")) and
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '[data-title="Browse Lots"], [data-track="page_nav|lots"]'))
        )
    except Exception as e:
        print(f"wait exception: {e}")


def get_auction_title(wd):
    try:

        auction_title_element = WebDriverWait(wd, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            ".chr-auction-header__auction-title"))
        )

        # auction_title_element = wd.find_element_by_css_selector(
        #     ".chr-auction-header__auction-title")

        return auction_title_element.text.lower()
    except Exception as e:
        print(f"auction title error: {e}")
        return ""

# def get_piece_titles(wd):
#     try:
#         title_elements = wd.find_elements_by_xpath(
#             "//*[@class='chr-lot-tile__primary-title']")

#         return [e.text.lower().strip() for e in title_elements]

#     except TimeoutException as e:
#         print(f"piece titles error {e}")
#         return []
#     except NoSuchElementException as e:
#         print(f"piece titles error {e}")
#         return []


def get_num_lots(wd):
    try:
        lot_num_text = WebDriverWait(wd, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            '[data-title="Browse Lots"], [data-track="page_nav|lots"]'))
        ).text

        # lot_num_text = wd.find_element_by_css_selector(
        #     '[data-title="Browse Lots"], [data-track="page_nav|lots"]').text

        return int(''.join(c for c in lot_num_text if c.isdigit()))
    except Exception as e:
        print(f"num lots error {e}")
        return 0


def scrape_auction(wd, link, keyword_dict):
    wd.get(link)

    accept_cookies()
    close_signup()
    scroll_to_bottom(wd)

    asian_piece_count = 0

    auction_title = get_auction_title(wd)
    print(f"\nAuction Title: {auction_title}")

    # piece_titles = get_piece_titles(wd)
    # print(f"\nPiece Title: {len(piece_titles)}")

    num_lots = get_num_lots(wd)
    print(f"\nNum Lots: {num_lots}")

    # super_keyword_set = set()

    match = False

    for keyword in keyword_dict:

        if keyword in auction_title:

            match = True

            keyword_dict[keyword] += num_lots
            # super_keyword_set.add(keyword)
            # print("SPECIAL!!!")

    if match:
        asian_piece_count += num_lots

    # for title in piece_titles:

    #     match = False

    #     for keyword in keyword_dict:

    #         if keyword in super_keyword_set:
    #             continue

    #         if keyword in title:
    #             match = True
    #             keyword_dict[keyword] += 1

    #     if match:
    #         asian_piece_count += 1

    return (asian_piece_count, num_lots)


def scrape_auctions(wd, auction_links, keyword_dict):

    asian_piece_count = 0
    total_piece_count = 0

    for link in auction_links:

        result = scrape_auction(wd, link, keyword_dict)
        asian_piece_count += result[0]
        total_piece_count += result[1]

        print(keyword_dict)

    return (asian_piece_count, total_piece_count)


def scrape_christies(year):

    print(f"FOR YEAR {year}\n")

    keyword_dict = {"chinese": 0,
                    "china": 0,
                    "korean": 0,
                    "korea": 0,
                    "japanese": 0,
                    "japan": 0,
                    "orient": 0,
                    "dynasty": 0,
                    "asian": 0,
                    "asia": 0,
                    "year": year}

    result_dict = {
        "asian_piece_count": 0,
        "total_piece_count": 0,
        "ratio": 0.0,
        "year": year,
    }

    base_url = "https://www.christies.com/en/results?"

    for month in range(1, 13):

        print(F"\nMONTH {month}\n")

        wd.get(f"{base_url}month={month}&year={year}")

        accept_cookies()
        close_signup()

        try:
            auction_link_elements = wd.find_elements_by_css_selector(
                ".chr-event-tile__title")

            auction_links = [e.get_attribute('href')
                             for e in auction_link_elements]

            result = scrape_auctions(wd,
                                     auction_links, keyword_dict)

            result_dict["asian_piece_count"] += result[0]
            result_dict["total_piece_count"] += result[1]
            result_dict["ratio"] = result_dict["asian_piece_count"] / \
                result_dict["total_piece_count"]

            print(result_dict)
            print(keyword_dict)

        except Exception as e:
            print(f"{e} for year {year} and month {month}")

    filename = "christies_auction_keywords.csv"
    fields = list(keyword_dict.keys())
    file_exists = os.path.isfile(filename)

    write_to_csv(filename, fields, file_exists, keyword_dict)

    filename = "christies_auction_overall.csv"
    fields = list(result_dict.keys())
    file_exists = os.path.isfile(filename)

    write_to_csv(filename, fields, file_exists, result_dict)


def write_to_csv(filename, fields, file_exists, data):
    with open(filename, 'a') as csvfile:
        # creating a csv dict writer object
        writer = csv.DictWriter(csvfile, fieldnames=fields)

        if not file_exists:
            writer.writeheader()  # file doesn't exist yet, write a header

        # writing data rows
        writer.writerows([data])


CHROMEDRIVER_PATH = "./drivers/chromedriver"
chrome_bin = os.environ.get("GOOGLE_CHROME_BIN", "chromedriver")
options = webdriver.ChromeOptions()
options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
options.add_argument("--headless")
wd = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,
                      options=options)

try:
    scrape_christies(sys.argv[1])
except Exception as e:
    print(e)

wd.quit()
