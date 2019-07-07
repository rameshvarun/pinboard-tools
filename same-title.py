#!/usr/bin/env python3
import click
import json
import urllib.parse
import requests
from collections import defaultdict


@click.command()
@click.option("--auth-token", required=True)
def no_title(auth_token):
    links = requests.get(
        "https://api.pinboard.in/v1/posts/all",
        params={"auth_token": auth_token, "format": "json"},
    ).json()

    articles_by_title = defaultdict(list)
    for link in links:
        articles_by_title[link["description"]].append(link["href"])

    for title, links in articles_by_title.items():
        if len(links) < 2:
            continue

        print(title)
        print("---------")
        for link in links:
            print(link)

        print()


if __name__ == "__main__":
    no_title()
