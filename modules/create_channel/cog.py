import os
from dotenv.main import load_dotenv
from discord.ext import commands

load_dotenv()
MYSTERY_HUNT_ROLE_ID = int(os.getenv("MYSTERY_HUNT_ROLE_ID"))


class CreateChannelCog(commands.Cog):
	"""Checks for `createchannel` command
	Creates channel in same category with given name"""

	def __init__(self, bot):
		self.bot = bot
		self.is_nsfw = True

	@commands.command(name="createchannel")
	@commands.has_role(MYSTERY_HUNT_ROLE_ID)
	async def createchannel(self, ctx, name: str = ""):
		"""Command to create channel in same category with given name"""
		# log command in console
		print("Received createchannel command")
		# check for channel name argument
		if len(name) > 0:
			# get guild and category
			guild = ctx.message.guild
			category = ctx.channel.category
			# reply to user
			await ctx.send(f"Creating channel {name} in {category}!")
			# create channel
			await guild.create_text_channel(name, category=category, nsfw=self.is_nsfw)
		# no argument passed
		else:
			# reply to user
			await ctx.send(f"You must specify a channel name!")


def setup(bot):
	bot.add_cog(CreateChannelCog(bot))
