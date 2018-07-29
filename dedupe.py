#!/usr/bin/env python3
import click
import pinboard
import shelve

from collections import defaultdict
import metadata_parser


def get_canonical_link(url):
    try:
        page = metadata_parser.MetadataParser(url=url)
        return page.get_discrete_url()
    except metadata_parser.NotParsableFetchError:
        return None
    except metadata_parser.NotParsable:
        return None


@click.command()
@click.option("--auth-token", required=True)
def dedupe(auth_token):
    pb = pinboard.Pinboard(auth_token)
    by_url = defaultdict(list)
    parse_cache = shelve.open(".parse_cache")

    with click.progressbar(pb.posts.all(), label="Finding duplicates...") as bar:
        for bookmark in bar:
            if bookmark.url not in parse_cache:
                parse_cache[bookmark.url] = get_canonical_link(bookmark.url)
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
