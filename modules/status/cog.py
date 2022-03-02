import nextcord
import random
from nextcord.ext import commands
from nextcord.ext.tasks import loop


class Status(commands.Cog, name="Status"):
    def __init__(self, bot: commands.Bot):
        self.__bot = bot
        self.status_list = (
            nextcord.Activity(type=nextcord.ActivityType.watching, name="you struggle 👀"),
            nextcord.Game(name="around with numbers‍"),
        )
        self.current_status = random.randint(0, len(self.status_list) - 1)

    @commands.Cog.listener()
    async def on_ready(self):
        """When discord is connected"""
        # Start loop
        self.status_loop.start()

    @loop(seconds=600)
    async def status_loop(self):
        """Loop to update status"""
        self.current_status = (self.current_status + 1) % len(self.status_list)
        await self.__bot.change_presence(activity=self.status_list[self.current_status])


def setup(bot):
    bot.add_cog(Status(bot))
