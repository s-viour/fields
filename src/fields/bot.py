from functools import partial
import discord
from discord import FFmpegPCMAudio, PCMVolumeTransformer


class Fields(discord.Client):
    def __init__(self, channel_ids, audio_path, volume, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_ids = channel_ids
        self.audio_path = audio_path
        self.volume = volume
        self.conns = []

    def loop_audio(self, connection):
        def on_error(error):
            self.loop_audio(connection)

        audio = PCMVolumeTransformer(
            FFmpegPCMAudio(self.audio_path, before_options="-stream_loop -1"),
            volume=self.volume,
        )
        connection.play(source=audio, after=on_error)

    async def on_ready(self):
        if not self.channel_ids:
            print("no channels supplied, quitting")
            await self.close()

        channels = map(self.get_channel, self.channel_ids)

        for c in channels:
            self.conns.append(await c.connect())
        for c in self.conns:
            self.loop_audio(c)
