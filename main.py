#!/usr/bin/env python3
import os
import re
from time import sleep

import requests


class Scraper:
    def __init__(self, base_url, cookies):
        self.base_url = base_url
        self.cookies = self.parse_cookies(cookies)

    @staticmethod
    def parse_cookies(cookies):
        return {
            name: value for name, value in [cookie.split("=") for cookie in cookies]
        }

    @staticmethod
    def print_progress_bar(
        iteration, total, prefix="", suffix="", decimals=1, length=50, fill="#"
    ):
        """
        iteration - current iteration (Int)
        total - total iterations (Int)
        prefix - prefix string (Str)
        suffix - suffix string (Str)
        decimals - positive number of decimals in percent complete (Int)
        length - character length of bar (Int)
        fill - bar fill character (Str)
        """
        percent = ("{0:." + str(decimals) + "f}").format(
            100 * (iteration / float(total))
        )
        filled_length = int(length * iteration // total)
        bar = fill * filled_length + "-" * (length - filled_length)
        print(f"\r{prefix} |{bar}| {percent}% {suffix}", end="\r")
        # Print New Line on Complete
        if iteration == total:
            print()

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
    parser.add_argument(
        "-m",
        "--mode",
        help="The mode to use. Can be either 'user' or 'site",
        choices=["user", "site"],
        required=True,
    )
    parser.add_argument("-u", "--user", help="The user ID url to scrape, e.g. 12345")
    parser.add_argument(
        "-s",
        "--section",
        help="The section to scrape. In the case of user mode, can only be either anime or music",
        choices=["anime", "music", "printed", "games"],
        required=True,
    )
    parser.add_argument(
        "total_pages", help="The max number of pages to scrape", type=int
    )

    args = parser.parse_args()

    if args.total_pages < 1:
        parser.error("Total pages must be greater than 0")

    if args.mode == "user" and not args.user:
        parser.error("User mode requires a user ID, set one with -u or --user")

    with open(args.cookies, "r") as f:
        cookies = f.read().strip().split(";")

    if args.mode == "user":
        base_url = f"https://animebytes.tv/alltorrents.php?userid={args.user}&type=seeding&order_by=size&order_way=ASC&section={args.section}&page="
    elif args.mode == "site":
        section_urls = {
            "music": "https://animebytes.tv/torrents2.php?filter_cat%5B1%5D=1&sort=size&way=asc&showhidden=0&page=",
            "anime": "https://animebytes.tv/torrents.php?filter_cat%5B1%5D=1&action=advanced&search_type=title&sort=size&way=asc&hentai=2&showhidden=0&page=",
            "printed": "https://animebytes.tv/torrents.php?filter_cat%5B2%5D=1&action=advanced&search_type=title&sort=size&way=asc&hentai=2&showhidden=0&page=",
            "games": "https://animebytes.tv/torrents.php?filter_cat%5B3%5D=1&action=advanced&search_type=title&sort=size&way=asc&hentai=2&showhidden=0&page=",
        }
        base_url = section_urls.get(args.section)

        if base_url is None:
            parser.error(
                "Invalid section, valid choices are 'music', 'anime', 'printed', and 'games'"
            )
    else:
        parser.error("Invalid mode")

    scraper = Scraper(base_url, cookies)

    all_links = []
    for page_number in range(1, args.total_pages + 1):
        page_links = scraper.scrape_links(page_number)
        all_links.extend(page_links)
        scraper.print_progress_bar(
            page_number,
            args.total_pages,
            prefix=f"Page {page_number}/{args.total_pages}:",
        )

        if page_number != args.total_pages:
            sleep(args.ratelimit)

    os.makedirs("output", exist_ok=True)
    filename = args.user if args.mode == "user" else args.section
    with open(f"output/{filename}.txt", "w") as f:
        f.write("\n".join(all_links))
