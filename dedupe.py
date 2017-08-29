#!/usr/bin/env python3
import click
import pinboard
import shelve

from collections import defaultdict

from mercury_parser.client import MercuryParser

@click.command()
@click.option('--auth-token', required=True)
@click.option('--mercury-api-key', required=True)
def dedupe(auth_token, mercury_api_key):
    pb = pinboard.Pinboard(auth_token)
    mercury = MercuryParser(api_key=mercury_api_key)
    parse_cache = shelve.open('.parse_cache')

    by_url = defaultdict(list)

    with click.progressbar(pb.posts.all(), label="Finding duplicates...") as bar:
        for bookmark in bar:
            if bookmark.url in parse_cache:
                parsed = parse_cache[bookmark.url]
            else:
                parsed = mercury.parse_article(bookmark.url)
                parse_cache[bookmark.url] = parsed
                parse_cache.sync()

            if not parsed: continue
            parsed = parsed.json()
            if 'url' not in parsed: continue

            by_url[parsed['url']].append(bookmark)

    parse_cache.close()

    count = 0
    for url, items in by_url.items(): count += max(len(items) - 1, 0)
    print(count, "possible duplicates.")

    for url, items in by_url.items():
        if len(items) < 2: continue
        print([i.description for i in items], " point to the same url:", url)
        if click.confirm('Do you want to delete the newer ones?'):
            items = sorted(items, key=lambda b: b.time)
            todelete = items[1:]
            print("Deleting ", todelete)
            for b in todelete:
                b.delete()

if __name__ == '__main__':
    dedupe()
