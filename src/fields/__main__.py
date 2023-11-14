import os
import sys
import json
import logging
import argparse
from .bot import Fields
from dotenv import load_dotenv
import discord

log = logging.getLogger("fields.main")


def main():
    """parses the config and environment, then starts the bot"""
    load_dotenv()

    args = _parse_args()
    _setup_logging(args.debug)

    token = os.getenv("BOT_TOKEN")
    if token is None:
        log.warning("missing `BOT_TOKEN` environment variable")
        return

    try:
        cfg = _read_config(args.config)
    except KeyError as e:
        print(f"invalid config: {e}", file=sys.stderr)
        return
    except FileNotFoundError:
        print(f"could not find `{args.config}`", file=sys.stderr)
        return

    intents = discord.Intents.default()
    client = Fields(
        intents=intents,
        channel_ids=cfg["channelIDs"],
        audio_path=cfg["audioPath"],
        volume=cfg["volume"],
    )
    # we disable the log_handler here to allow our _setup_logging function
    # to give the logger its own config
    client.run(token, log_handler=None)


def _parse_args():
    """handles the creation of and execution of the `ArgumentParser`"""
    parser = argparse.ArgumentParser(
        prog="fields",
        description="discord bot that plays ambience. forever",
    )

    parser.add_argument("-c", "--config", default="config.json")
    parser.add_argument("-d", "--debug", action="store_true")
    return parser.parse_args()


def _read_config(filename):
    """read and validates the passed config file. assumes that the file exists.
    if the file does not exist, `open` will throw a `FileNotFoundError`
    """
    with open(filename) as f:
        j = json.load(f)
        if "channelIDs" not in j or "audioPath" not in j:
            raise KeyError("missing key `channelIDs`")
        elif "audioPath" not in j:
            raise KeyError("missing key `audioPath`")
        elif "volume" not in j:
            raise KeyError("missing key `volume`")
        return j


def _setup_logging(debug=False):
    """sets up the fields logger"""
    level = logging.DEBUG if debug else logging.INFO
    log_format = "[%(asctime)s %(levelname)s %(name)s] %(message)s"
    ch = logging.StreamHandler()
    logging.basicConfig(format=log_format, handlers=[ch], level=level)


if __name__ == "__main__":
    main()
