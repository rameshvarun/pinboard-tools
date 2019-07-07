#!/usr/bin/env python3
import click
import pinboard
from urllib.parse import urlparse

VIDEO_HOSTNAMES = set(
    ["www.vimeo.com", "vimeo.com", "www.youtube.com", "youtube.com", "youtu.be"]
)


@click.command()
@click.option("--auth-token", required=True)
def tag_videos(auth_token):
    pb = pinboard.Pinboard(auth_token)

    with click.progressbar(pb.posts.all(), label="Finding videos...") as bar:
        for bookmark in bar:
            hostname = urlparse(bookmark.url).hostname
            if hostname in VIDEO_HOSTNAMES:
                if "video" not in bookmark.tags:
                    bookmark.tags.append("video")
                    bookmark.save()


if __name__ == "__main__":
    tag_videos()
