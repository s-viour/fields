import logging
from functools import partial
import asyncio
import discord
from discord import FFmpegPCMAudio, PCMVolumeTransformer


log = logging.getLogger("fields.bot")


class Fields(discord.Client):
    """class implementing the single-bot fields functionality"""

    def __init__(
        self, channel_ids, audio_path, volume, check_timeout=60, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.channel_ids = channel_ids
        self.audio_path = audio_path
        self.volume = volume
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

        # add the connection manager to the event loop
        # this will periodically run every 5s
        self.loop.create_task(self.manage_connections())

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
