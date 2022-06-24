import os
import sys
import json
from functools import partial
from discord import FFmpegPCMAudio, PCMVolumeTransformer
from discord.ext import commands


def read_config():
    try:
        with open('config.json') as f:
            j = json.load(f)
            if 'channelIDs' not in j:
                print('invalid config: missing key channelIDs')
                raise SystemExit
            elif 'audioPath' not in j:
                print('invalid config: missing key audioPath')
                raise SystemExit
            return j
    except json.JSONDecodeError as e:
        print(f'config file not found: {e}')


def loop_audio(path, connection, e=None):
    audio = PCMVolumeTransformer(FFmpegPCMAudio(path))
    cb = partial(loop_audio, path, connection)
    connection.play(source=audio, after=cb)


bot = commands.Bot(command_prefix='$')


@bot.event
async def on_ready():
    channel_ids = bot.config['channelIDs']
    audio_path = bot.config['audioPath']

    if channel_ids == []:
        print('no channels supplied, quitting')
        await bot.close()
    
    channels = map(bot.get_channel, channel_ids)
    
    conns = []
    for c in channels:
        conns.append(await c.connect())
    for c in conns:
        loop_audio(audio_path, c)


def main():
    enable_server = False
    if len(sys.argv) > 0:
        enable_server = sys.argv[0] == '--server'
    
    token = os.getenv('BOT_TOKEN')
    if token is None:
        print('no token supplied\nmust be set to environment variable BOT_TOKEN', file=sys.stderr)
        return

    if enable_server:
        from server import keep_alive
        keep_alive()
    bot.config = read_config()
    bot.run(token)

if __name__ == '__main__':
    main()
