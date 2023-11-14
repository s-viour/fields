import os
import sys
import json
import logging
from .bot import Fields
from dotenv import load_dotenv
import discord

log = logging.getLogger("fields.main")


def main():
    """parses the config and environment, then starts the bot"""
    load_dotenv()

    token = os.getenv("BOT_TOKEN")
    if token is None:
        log.warning("missing `BOT_TOKEN` environment variable")
        return

    try:
        cfg = _read_config()
    except KeyError as e:
        print(f"invalid config: {e}", file=sys.stderr)
        return
    except FileNotFoundError:
        print("could not find `config.json`", file=sys.stderr)
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


def _read_config():
    """read and validates the `config.json` file. assumes that the file exists.
    if the file does not exist, `open` will throw a `FileNotFoundError`
    """
    with open("config.json") as f:
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
    debug = "--debug" in sys.argv or "-d" in sys.argv
    _setup_logging(debug)
    main()
