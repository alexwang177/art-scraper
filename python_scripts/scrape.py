#!/usr/bin/env python
from selenium import webdriver
from PIL import Image
import requests
import hashlib
import io
import time
import os
import sys


def fetch_image_urls(query: int, max_links_to_fetch: int, wd: webdriver, sleep_between_interactions: int = 1):
    def scroll_to_end(wd):
        wd.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)

    # build the google query
    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

    # load the page
    wd.get(search_url.format(q=query))

    image_urls = set()
    image_count = 0
    results_start = 0

    while image_count < max_links_to_fetch:

        scroll_to_end(wd)

        # get all image thumbnail results
        thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
        number_results = len(thumbnail_results)

        print(
            f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")

        for img in thumbnail_results[results_start:number_results]:
            # try to click every thumbnail to get real image
            try:
                img.click()
                time.sleep(sleep_between_interactions)
            except Exception:
                print("img click issue")
                continue

            # extract image urls
            actual_images = wd.find_elements_by_css_selector("img.n3VNCb")
            for actual_image in actual_images:
                if actual_image.get_attribute("src") and "http" in actual_image.get_attribute("src"):
                    image_urls.add(actual_image.get_attribute("src"))

            image_count = len(image_urls)

            if len(image_urls) >= max_links_to_fetch:
                print(f"Found: {len(image_urls)} links, done!")
                break
            else:
                print("Found:", len(image_urls),
                      "image links, looking for more...")
                time.sleep(0.01)

        load_more_button = wd.find_element_by_css_selector(".mye4qd")
        if load_more_button:
            wd.execute_script("document.querySelector('.mye4qd').click();")

        # move result start point
        results_start = len(thumbnail_results)

    return image_urls


def persist_image(folder_path: str, url: str):

    print("before request")

    try:
        image_content = requests.get(url, timeout=5).content
    except Exception as e:
        print(f"Error - Could not download {url} - {e}")

    print("after request, before saving")

    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert("RGB")
        file_path = os.path.join(folder_path, hashlib.sha1(
            image_content).hexdigest()[:10] + ".jpg")

        with open(file_path, "wb") as f:
            image.save(f, "JPEG", quality=85)
        print(f"Success - saved {url} - as {file_path}")

    except Exception as e:
        print(f"Error - Could not save {url} - {e}")

    print("after saving")


def search_and_download(search_term: str, driver_path: str, wd: webdriver, target_path="./images", number_images=30):
    target_folder = os.path.join(
        target_path, "_".join(search_term.lower().split(" ")))

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    try:
        # with webdriver.Chrome(executable_path=driver_path) as wd:
        try:
            url_set = fetch_image_urls(
                search_term, number_images, wd=wd, sleep_between_interactions=0.5)
        except Exception as e:
            print(f"fetch_image_urls function call error - {e}")
    except Exception as e:
        print(f"webdriver fetch issue - {e}")

    for url in url_set:
        try:
            persist_image(target_folder, url=url)
        except Exception as e:
            print(f"persist image error - {e}")


try:
    print(sys.argv[1])
except:
    print("sys error")

CHROMEDRIVER_PATH = "./drivers/chromedriver"
#CHROMEDRIVER_PATH = "/app/.chromedriver/bin/chromedriver"
chrome_bin = os.environ.get("GOOGLE_CHROME_BIN", "chromedriver")
options = webdriver.ChromeOptions()
options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
# options.add_argument("--disable-gpu")
# options.add_argument("--no-sandbox")
# options.add_argument("--headless")
# options.add_argument('--disable-dev-shm-usage')
# options.add_argument("--example-flag")
# options.add_argument('--window-size=1280x1696')
# options.add_argument('--hide-scrollbars')
# options.add_argument('--single-process')
# options.add_argument('--ignore-certificate-errors')
wd = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,
                      options=options)

# Now you can start using Selenium

# wd = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH)

try:
    search_and_download(
        sys.argv[1], driver_path=CHROMEDRIVER_PATH, wd=wd, number_images=int(sys.argv[2]))
except:
    print("search and download error")

wd.quit()
