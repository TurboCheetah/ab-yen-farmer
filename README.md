# ab-yen-farmer

Scripts to scrape torrents from AnimeBytes, either from a user's profile or from the entire site.

## Usage

Make sure that you have [Poetry](https://python-poetry.org/docs/#installation) installed.
You must copy `config.example.toml` to `config.toml` and enter a valid cookie.

### Scrape from a user's profile

```bash
poetry run farm -m user -u <user id> -s <section> <pages>
```

### Scrape from the entire site

Due to the way in which AnimeBytes groups torrents, scraping the entire site, even when sorted by filesize, will include the links to every torrent in the group.
For example, if a group contains a 2MB torrent and a 2GB torrent, both links will be saved.

```bash
poetry run farm -m site -s <section> <pages>
```
