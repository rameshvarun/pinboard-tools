#!/usr/bin/env python3
import click
import pinboard
import shelve
import os

from collections import defaultdict
import metadata_parser
from urllib.parse import urlparse, parse_qs


def get_canonical_link(url):
    try:
        page = metadata_parser.MetadataParser(url=url)
        return page.get_discrete_url()
    except metadata_parser.NotParsableFetchError:
        return None
    except metadata_parser.NotParsable:
        return None

def get_youtube_id(url):
    parsed = urlparse(url)
    if parsed.hostname == "youtu.be":
        return f"youtube-vid:{parsed.path[1:]}"
    if parsed.hostname == "www.youtube.com":
        if parsed.path == "/watch":
            vid = parse_qs(parsed.query)["v"][0]
            return f"youtube-vid:{vid}"


def get_arxiv_id(url):
    parsed = urlparse(url)
    if parsed.hostname == "arxiv.org":
        head, tail = os.path.split(parsed.path)
        if head == "/abs":
            return f"arxiv:{tail}"
        if head == "/pdf":
            name, ext = os.path.splitext(tail)
            return f"arxiv:{name}"

NORMALIZERS = [get_youtube_id, get_arxiv_id]

def normalize_url(url):
    normalized_id = None
    for normalizer in NORMALIZERS:
        normalized_id = normalizer(url)
        if normalized_id:
            break
    return normalized_id


@click.command()
@click.option("--auth-token", required=True)
def dedupe(auth_token):
    pb = pinboard.Pinboard(auth_token)
    by_url = defaultdict(list)
    parse_cache = shelve.open(".parse_cache")

    with click.progressbar(pb.posts.all(), label="Finding duplicates...") as bar:
        for bookmark in bar:
            if bookmark.url not in parse_cache:
                parse_cache[bookmark.url] = normalize_url(bookmark.url)
                parse_cache.sync()

            canonical = parse_cache[bookmark.url]
            if canonical:
                by_url[canonical].append(bookmark)

    parse_cache.close()

    count = 0
    for url, items in by_url.items():
        count += max(len(items) - 1, 0)
    print(count, "possible duplicates.")

    for url, items in by_url.items():
        if len(items) < 2:
            continue
        print([i.description for i in items], " point to the same url:", url)
        if click.confirm("Do you want to delete the newer ones?"):
            items = sorted(items, key=lambda b: b.time)
            todelete = items[1:]
            print("Deleting ", todelete)
            for b in todelete:
                b.delete()


if __name__ == "__main__":
    dedupe()
