#!/usr/bin/env python3
import re
from time import sleep

import requests


class Scraper:
    def __init__(self, user_id, section, cookies):
        self.user_id = user_id
        self.section = section
        self.base_url = f"https://animebytes.tv/alltorrents.php?userid={self.user_id}&type=seeding&order_by=size&order_way=ASC&section={self.section}&page="
        self.cookies = self.parse_cookies(cookies)

    def parse_cookies(self, cookies):
        return {
            name: value for name, value in [cookie.split("=") for cookie in cookies]
        }

    def scrape_links(self, page_number):
        url = self.base_url + str(page_number)
        response = requests.get(url, cookies=self.cookies)

        if response.status_code == 200:
            pattern = re.compile(r"/torrent/\d*/download/[^\"]*")
            links = pattern.findall(response.text)
            return ["https://animebytes.tv" + link for link in links]
        else:
            print(f"Error {response.status_code}: Unable to access page {page_number}")
            return []


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--cookies",
        help="The cookie file to use",
        default="cookies.txt",
    )
    parser.add_argument(
        "-r",
        "--ratelimit",
        help="The amount of time to wait between requests",
        default=5,
        type=int,
    )
    parser.add_argument("user_id", help="The user ID url to scrape, e.g. 12345")
    parser.add_argument("section", help="The section to scrape, e.g. anime or music")
    parser.add_argument(
        "total_pages", help="The max number of pages to scrape", type=int
    )

    args = parser.parse_args()

    # Parse cookies from the file passed into args.cookies
    with open(args.cookies, "r") as f:
        cookies = f.read().strip().split(";")

    scraper = Scraper(args.user_id, args.section, cookies)

    all_links = []
    for page_number in range(1, args.total_pages + 1):
        page_links = scraper.scrape_links(page_number)
        all_links.extend(page_links)
        print(f"Scraped {len(page_links)} links from page {page_number}")
        sleep(args.ratelimit)

    # Save the links to a file
    with open("links.txt", "w") as f:
        for link in all_links:
            f.write(link + "\n")
