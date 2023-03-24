import os
import re
import tomllib
from time import sleep

import requests
from tqdm import tqdm


class Scraper:
    def __init__(self, base_url, cookie):
        self.base_url = base_url
        self.cookie = cookie

    def scrape_links(self, page_number):
        url = self.base_url + str(page_number)
        response = requests.get(url, cookies=self.cookie)

        if response.status_code == 200:
            pattern = re.compile(r"/torrent/\d*/download/[^\"]*")
            links = pattern.findall(response.text)
            return ["https://animebytes.tv" + link for link in links]
        else:
            print(f"Error {response.status_code}: Unable to access page {page_number}")
            return []


def main():
    import argparse

    parser = argparse.ArgumentParser()
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

    with open("config.toml", "rb") as f:
        config = tomllib.load(f)
        cookie = config.get("cookie")
        if not cookie:
            parser.error("No cookie found in config.toml")
        cookie = {cookie.split("=")[0]: cookie.split("=")[1]}

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

    scraper = Scraper(base_url, cookie)

    os.makedirs("output", exist_ok=True)
    filename = args.user if args.mode == "user" else args.section
    output_path = f"output/{filename}.txt"

    # Check if the output file exists and read the existing links into a set
    existing_links = set()
    if os.path.exists(output_path):
        with open(output_path, "r") as f:
            existing_links = set(f.read().splitlines())

    all_links = []
    for page_number in tqdm(
        range(1, args.total_pages + 1),
        bar_format="Page {n}/{total} {bar} {percentage:0.1f}%",
    ):
        page_links = scraper.scrape_links(page_number)
        # Check if each link exists in the output file and if not, add it to the set
        # and write it to the output file
        with open(output_path, "a") as f:
            for link in page_links:
                if link not in existing_links:
                    all_links.append(link)
                    existing_links.add(link)
                    f.write(f"{link}\n")

        if page_number != args.total_pages:
            sleep(args.ratelimit)


if __name__ == "__main__":
    main()
