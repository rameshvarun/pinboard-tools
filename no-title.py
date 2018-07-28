#!/usr/bin/env python3
import click
import json
import requests
import time
import sys
from mercury_parser.client import MercuryParser
from urlextract import URLExtract
import urllib

extractor = URLExtract()


def is_url(text):
    urls = extractor.find_urls(text)
    return len(urls) == 1 and len(urls[0]) == len(text)


@click.group()
def cli():
    pass


def has_no_title(link):
    if link["description"] == False:
        return True
    if is_url(link["description"]):
        return True
    return False


@cli.command()
@click.option("--auth-token", required=True)
def list(auth_token):
    username = auth_token.split(":")[0]

    links = requests.get(
        "https://api.pinboard.in/v1/posts/all",
        params={"auth_token": auth_token, "format": "json"},
    ).json()

    links = [l for l in links if has_no_title(l)]

    print(len(links), "articles without a title...")
    print("------------------")
    for link in links:
        print(
            f"https://pinboard.in/search/u:{username}?query={urllib.parse.quote(link['href'])}"
        )


@cli.command("add-titles")
@click.option("--auth-token", required=True)
@click.option("--mercury-api-key", required=True)
def add_titles(auth_token, mercury_api_key):
    parser = MercuryParser(api_key=mercury_api_key)

    links = requests.get(
        "https://api.pinboard.in/v1/posts/all",
        params={"auth_token": auth_token, "format": "json"},
    ).json()

    for link in links:
        if has_no_title(link):
            res = parser.parse_article(link["href"])
            if res:
                parsed = res.json()
                if parsed["title"] is None or parsed["title"].strip() == "":
                    print(f"Can't find title for {link['href']}... Skipping...")
                    continue

                if click.confirm(
                    f"Do you want to change the title of {link['href']} to \"{parsed['title']}\"?"
                ):
                    res = requests.get(
                        "https://api.pinboard.in/v1/posts/add",
                        params={
                            "auth_token": auth_token,
                            "url": link["href"],
                            "description": parsed["title"],
                            "format": "json",
                            "extended": link["extended"],
                            "toread": link["toread"],
                            "tags": link["tags"],
                            "shared": link["shared"],
                        },
                    )


if __name__ == "__main__":
    cli()
