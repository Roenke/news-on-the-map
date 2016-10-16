import argparse
import json
import os
import time
import rss


def create_parser():
    parser = argparse.ArgumentParser('')
    parser.add_argument("--config", required=True, type=str,
                        help="path to crawler config file")
    return parser


def put_into_db(text, date, url):
    print url, ":", date


loaders = {
    "rss": rss.load
}


def main():
    args = create_parser().parse_args()

    if not os.path.exists(args.config):
        raise Exception("config doesn't exists")

    with open(args.config, "r") as f:
        config = json.load(f)

    while True:
        for link in config["links"]:
            t = link["type"]
            for (text, data, url) in loaders[t](link["url"]):
                put_into_db(text, data, url)

        time.sleep(config["period"])

if __name__ == "__main__":
    main()
