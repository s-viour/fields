import os
import sys
import json
import logging
from bot import Fields
from dotenv import load_dotenv
import discord


def main():
    load_dotenv()

    token = os.getenv("BOT_TOKEN")
    if token is None:
        print("missing `BOT_TOKEN` environment variable", file=sys.stderr)
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
    client.run(token)

def _read_config():
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
    ch = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s %(levelname)s %(name)s] %(message)s")
    ch.setFormatter(formatter)
    log = logging.getLogger()
    log.setLevel(level)
    log.addHandler(ch)

if __name__ == "__main__":
    debug = "--debug" in sys.argv or "-d" in sys.argv
    _setup_logging(debug)
    main()

