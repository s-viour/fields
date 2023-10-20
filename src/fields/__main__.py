import os
import sys
import json
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
        cfg = read_config()
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


def read_config():
    with open("config.json") as f:
        j = json.load(f)
        if "channelIDs" not in j or "audioPath" not in j:
            raise KeyError("missing key `channelIDs`")
        elif "audioPath" not in j:
            raise KeyError("missing key `audioPath`")
        elif "volume" not in j:
            raise KeyError("missing key `volume`")
        return j


if __name__ == "__main__":
    main()
