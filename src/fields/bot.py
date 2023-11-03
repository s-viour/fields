import logging
from functools import partial
import asyncio
import discord
from discord import FFmpegPCMAudio, PCMVolumeTransformer


log = logging.getLogger("fields.bot")


class Fields(discord.Client):
    def __init__(self, channel_ids, audio_path, volume, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_ids = channel_ids
        self.audio_path = audio_path
        self.volume = volume
        self.conns = []

    def loop_audio(self, connection):
        audio = PCMVolumeTransformer(
            FFmpegPCMAudio(self.audio_path, before_options="-stream_loop -1"),
            volume=self.volume,
        )
        connection.play(source=audio)

    def is_all_connected(self):
        conn_status = list(map(lambda c: c.is_connected(), self.conns))
        log.debug(f"conn_status: {conn_status}")
        if conn_status == []:
            return True
        return all(conn_status)

    async def on_ready(self):
        if not self.channel_ids:
            log.error("no channels supplied! quitting...")
            await self.close()

        self.channels = map(self.get_channel, self.channel_ids)
        for c in self.channels:
            self.conns.append(await c.connect())
        for c in self.conns:
            self.loop_audio(c)
        

    async def on_voice_state_update(self, member, before, after):
        if self.user != member: 
            return

        while not self.is_all_connected():
            await asyncio.sleep(1)

        for c in self.conns:
            c.stop()
            self.loop_audio(c)

