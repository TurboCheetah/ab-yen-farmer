# ab-yen-farmer

Scripts to scrape torrents from AnimeBytes, either from a user's profile or from the entire site.

## Usage

You must put your session cookie into a file called `cookies.txt` in the following format: `session=...`

### Scrape from a user's profile

```bash
./main.py -m user -u <user id> -s <section> <pages>
```

### Scrape from the entire site

Due to the way in which AnimeBytes groups torrents, scraping the entire site, even when sorted by filesize, will include the links to every torrent in the group.
For example, if a group contains a 2MB torrent and a 2GB torrent, both links will be saved.

```bash
./main.py -m site -s <section> <pages>
```
