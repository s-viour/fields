import logging
from functools import partial
import asyncio
import discord
import random
from discord import FFmpegPCMAudio, PCMVolumeTransformer


log = logging.getLogger("fields.bot")


class Fields(discord.Client):
    """class implementing the single-bot fields functionality"""

    def __init__(
        self, channel_ids, audio_path, volume, check_timeout=60, mode="loop", chance=1, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.channel_ids = channel_ids
        self.audio_path = audio_path
        self.volume = volume
        self.mode = mode
        self.chance = chance
        self.channels = []
        self.conns = []
        self.check_timeout = check_timeout

    def loop_audio(self, connection):
        """begin looping the Fields' audio forever on a `discord.VoiceClient`"""
        log.info(f"playing audio on connection: {connection.channel}")
        audio = PCMVolumeTransformer(
            # the option "-stream_loop -1" loops the audio *forever*
            FFmpegPCMAudio(self.audio_path, before_options="-stream_loop -1"),
            volume=self.volume,
        )
        connection.play(source=audio)

    async def play_audio(self, connection):
        """play audio by itself. used by the `manage_connections` coroutine for
        the random mode
        """

        log.info(f"playing audio on connection: {connection.channel}")
        audio = PCMVolumeTransformer(
            FFmpegPCMAudio(self.audio_path),
            volume=self.volume
        )
        connection.play(source=audio)
        while True:
            if not connection.is_playing():
                return
            await asyncio.sleep(1)

    async def manage_connections(self):
        """coroutine that runs forever on the discord event loop.
        responsible for starting audio on connections whenever that connection
        does not currently have audio playing.
        """
        while True:
            # run forever and attempt to find connections that aren't playing
            for c in self.conns:
                if c.is_connected() and c.is_playing():
                    # these are all known methods to check if a connection is okay
                    # discord is a volatile beast though and there may be cases
                    # this method can't detect
                    continue

                log.warn(
                    f'connection to "{c.channel.name}" is not playing audio. starting audio'
                )
                # always call stop first just in case the connection *thinks* it's playing
                # this happens whenever a server region changes
                c.stop()
                self.loop_audio(c)

            await asyncio.sleep(5)

    async def manage_random(self):
        """connection manager for the random mode
        """
        while True:
            if not roll_chance(self.chance):
                await asyncio.sleep(5)
                continue

            await self.join_all_channels()
            for c in self.conns:
                await self.play_audio(c)
                await c.disconnect()

            await asyncio.sleep(5)

    async def join_all_channels(self):
        """clears the channels and conns list, then connects to all of them
        """
        self.channels.clear()
        self.conns.clear()

        self.channels = list(map(self.get_channel, self.channel_ids))
        for c in self.channels:
            self.conns.append(await c.connect())

    async def on_ready(self):
        """function that runs when the bot starts. will create all connections and begin
        looping audio on all of them immediately
        """
        if not self.channel_ids:
            log.error("no channels supplied! quitting...")
            await self.close()

        if self.mode == "loop":
            await self.join_all_channels()
            self.loop.create_task(self.manage_connections())
        else:
            self.loop.create_task(self.manage_random())

    async def on_voice_state_update(self, member, before, after):
        """implemented specifically to restart the audio streams when the
        server region changes or the bots are disconnected and reconnected for some reason
        """

        # ignore all voice state updates that don't pertain to us
        if self.user != member:
            return

        # find connection belonging to server where our voice state was updated
        conn = None
        for c in self.conns:
            if member.guild == c.guild:
                conn = c

        if conn is None:
            log.warn(f"was unable to find connection belonging to {member.guild.name}")
            return

        conn.stop()


def roll_chance(chance):
    return random.random() <= chance