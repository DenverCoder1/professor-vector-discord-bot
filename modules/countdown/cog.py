import config
import discord
from discord.errors import HTTPException
from discord.ext import commands
from discord.ext.tasks import loop

from .countdown import (
    get_last_countdown,
    get_updated_content,
    message_has_command,
    create_countdown,
)


class Countdown(commands.Cog, name="Countdown"):
    def __init__(self, bot: commands.Bot):
        self.__bot = bot
        self.__channel = None

    @commands.Cog.listener()
    async def on_ready(self):
        """When discord is connected"""
        if self.__channel:
            return
        # get clock channel object
        self.__channel = self.__bot.get_channel(config.ANNOUNCEMENTS_CHANNEL_ID)
        # check that channel exists
        if not isinstance(self.__channel, discord.TextChannel):
            raise LookupError("Couldn't find that channel.")
        # if channel exists, get the last countdown message from the bot
        self.__message = await get_last_countdown(self.__channel)
        if not self.__message:
            return
        # Start clock
        self.countdown.start()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """When discord is connected"""
        if message.channel != self.__channel:
            return
        if message_has_command(message):
            self.__message = await create_countdown(message)
            if not self.countdown.is_running():
                self.countdown.start()

    @loop(seconds=30)
    async def countdown(self):
        """Loop to check and update clock"""
        # update the clock message
        try:
            new_content = get_updated_content(self.__message)
            # update only if the time is different
            if new_content != self.__message.content:
                # edit the message
                await self.__message.edit(content=new_content)
        except HTTPException:
            # if message doesn't exist, cancel the loop
            self.countdown.cancel()

    @countdown.before_loop
    async def clock_init(self) -> None:
        """print startup info"""
        print("Starting countdown...")


def setup(bot):
    bot.add_cog(Countdown(bot))
