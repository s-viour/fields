import logging
from functools import partial
import asyncio
import discord
from discord import FFmpegPCMAudio, PCMVolumeTransformer


log = logging.getLogger("fields.bot")


class Fields(discord.Client):
    """class implementing the single-bot fields functionality"""
    def __init__(self, channel_ids, audio_path, volume, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_ids = channel_ids
        self.audio_path = audio_path
        self.volume = volume
        self.conns = []

    def loop_audio(self, connection):
        """begin looping the Fields' audio forever on a `discord.VoiceClient`"""
        log.info(f"playing audio on connection: {connection.channel}")
        audio = PCMVolumeTransformer(
            # the option "-stream_loop -1" loops the audio *forever*
            FFmpegPCMAudio(self.audio_path, before_options="-stream_loop -1"),
            volume=self.volume,
        )
        connection.play(source=audio)

    def is_all_connected(self):
        """checks whether or not all `VoiceClient`s in `self.conns` are connected
        to a voice channel
        """
        conn_status = list(map(lambda c: c.is_connected(), self.conns))
        if conn_status == []:
            return True
        return all(conn_status)

    async def on_ready(self):
        """function that runs when the bot starts. will create all connections and begin
        looping audio on all of them immediately
        """
        if not self.channel_ids:
            log.error("no channels supplied! quitting...")
            await self.close()

        self.channels = map(self.get_channel, self.channel_ids)
        for c in self.channels:
            self.conns.append(await c.connect())
        for c in self.conns:
            self.loop_audio(c)
        

    async def on_voice_state_update(self, member, before, after):
        """implemented specifically to restart the audio streams when the
        server region changes or the bots are disconnected and reconnected for some reason
        """

        # ignore all voice state updates that don't pertain to us
        if self.user != member: 
            return

        # wait for all connections to actually get reconnected before
        # we attempt to play audio on all
        while not self.is_all_connected():
            await asyncio.sleep(1)

        for c in self.conns:
            # this stop is necessary!
            # whenever we get disconnected, discord doesn't inform us that we stopped
            # playing audio
            c.stop()
            self.loop_audio(c)

