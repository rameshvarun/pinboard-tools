#!/usr/bin/env python3
import click
import json
import requests
import time
import sys
import pinboard
import metadata_parser
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
    if link.description == None:
        return True
    if link.description == "":
        return True
    if link.description == "[no title]":
        return True
    if link.description == "untitled":
        return True
    if is_url(link.description):
        return True
    return False


@cli.command("list")
@click.option("--auth-token", required=True)
def list(auth_token):
    username = auth_token.split(":")[0]
    pb = pinboard.Pinboard(auth_token)

    links = pb.posts.all()
    links = [l for l in links if has_no_title(l)]

    print(len(links), "articles without a title...")
    print("------------------")
    for link in links:
        print(
            f"https://pinboard.in/search/u:{username}?query={urllib.parse.quote(link.url)}"
        )


@cli.command("add-titles")
@click.option("--auth-token", required=True)
def add_titles(auth_token):
    pb = pinboard.Pinboard(auth_token)
    links = pb.posts.all()
    links = [l for l in links if has_no_title(l)]

    for link in links:
        try:
            page = metadata_parser.MetadataParser(url=link.url)
            title = page.get_metadatas("title")[0]
            if title == None or title == "":
                raise Exception("Parsed title is empty.")
            if click.confirm(
                f'Do you want to change the title of {link.url} to "{title}"?'
            ):
                link.description = title
                link.save()
        except:
            print(f"Could not get title of {link.url}...")


if __name__ == "__main__":
    cli()
