#!/usr/bin/env python3
import click
import json
import requests
import time
import sys
from mercury_parser.client import MercuryParser

@click.group()
def cli(): pass

@cli.command()
@click.option('--auth-token', required=True)
def list(auth_token):
    links = requests.get('https://api.pinboard.in/v1/posts/all', params={
        'auth_token': auth_token,
        'format': 'json',
    }).json()

    links = [l for l in links if l['href'] == l['description']]

    print(len(links), "articles without a title...")
    print("------------------")
    for link in links:
        print("No title:", link['description'])

@cli.command('add-titles')
@click.option('--auth-token', required=True)
@click.option('--mercury-api-key', required=True)
def add_titles(auth_token, mercury_api_key):
    parser = MercuryParser(api_key=mercury_api_key)

    links = requests.get('https://api.pinboard.in/v1/posts/all', params={
        'auth_token': auth_token,
        'format': 'json',
    }).json()

    for link in links:
        href, title = link['href'], link['description']
        if href == title:
            print("No title:", href)
            res = parser.parse_article(href)
            if res:
                parsed = res.json()
                print(parsed['title'])
                time.sleep(1)

                res = requests.get('https://api.pinboard.in/v1/posts/add', params={
                    'auth_token': auth_token,
                    'url': href,
                    'description': parsed['title'],
                    'format': 'json',

                    'extended': link['extended'],
                    'toread': link['toread'],
                    'tags': link['tags'],
                    'shared': link['shared'],
                })

if __name__ == '__main__':
    cli()
